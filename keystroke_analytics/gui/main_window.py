"""
Main GUI window.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

from PySide6.QtGui import QCloseEvent, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QDialog,
    QFileDialog,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from keystroke_analytics.gui.controller import EngineController, GuiConfigOverrides
from keystroke_analytics.gui.dialogs import ConsentDialog, PassphraseDialog

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    def __init__(
        self,
        config_path: Optional[Path],
        log_dir: Optional[Path],
        encrypt: bool,
        analytics_enabled: bool,
    ) -> None:
        super().__init__()
        self.setWindowTitle("Keystroke Analytics (Idle)")

        self._config_path = config_path
        self._log_dir = log_dir
        self._encrypt = encrypt
        self._analytics_enabled = analytics_enabled

        self._controller = EngineController()
        self._controller.started.connect(self._on_started)
        self._controller.stopped.connect(self._on_stopped)
        self._controller.error.connect(self._on_error)

        self._status = QLabel("Status: Idle")
        self._log_dir_label = QLabel(f"Log Dir: {self._log_dir or 'default'}")
        self._enc_label = QLabel(f"Encryption: {'ON' if self._encrypt else 'OFF'}")

        self._btn_start = QPushButton("Start Capture")
        self._btn_stop = QPushButton("Stop Capture")
        self._btn_stop.setEnabled(False)

        self._btn_choose_log = QPushButton("Choose Log Directory")

        self._btn_start.clicked.connect(self._start_clicked)
        self._btn_stop.clicked.connect(self._stop_clicked)
        self._btn_choose_log.clicked.connect(self._choose_log_dir)

        # Optional panic stop shortcut
        self._panic = QShortcut(QKeySequence("Ctrl+Shift+Q"), self)
        self._panic.activated.connect(self._stop_clicked)

        layout = QVBoxLayout()
        layout.addWidget(self._status)
        layout.addWidget(self._log_dir_label)
        layout.addWidget(self._enc_label)
        layout.addWidget(self._btn_choose_log)
        layout.addWidget(self._btn_start)
        layout.addWidget(self._btn_stop)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def _choose_log_dir(self) -> None:
        directory = QFileDialog.getExistingDirectory(self, "Select Log Directory")
        if directory:
            self._log_dir = Path(directory)
            self._log_dir_label.setText(f"Log Dir: {self._log_dir}")

    def _start_clicked(self) -> None:
        consent = ConsentDialog()
        if consent.exec() != QDialog.Accepted or not consent.accepted_with_consent():
            QMessageBox.warning(self, "Consent Required", "Consent not given.")
            return

        passphrase = None
        if self._encrypt:
            dlg = PassphraseDialog()
            if dlg.exec() != QDialog.Accepted:
                return
            passphrase = dlg.passphrase()
            if not passphrase:
                QMessageBox.warning(self, "Passphrase Required", "Passphrase is required.")
                return

        overrides = GuiConfigOverrides(
            config_path=self._config_path,
            log_dir=self._log_dir,
            encrypt=self._encrypt,
            analytics_enabled=self._analytics_enabled,
            passphrase=passphrase,
        )
        self._controller.start(overrides)

    def _stop_clicked(self) -> None:
        self._controller.stop()

    def _on_started(self) -> None:
        self._status.setText("Status: Recording")
        self.setWindowTitle("Keystroke Analytics (Recording)")
        self._btn_start.setEnabled(False)
        self._btn_stop.setEnabled(True)

    def _on_stopped(self) -> None:
        self._status.setText("Status: Idle")
        self.setWindowTitle("Keystroke Analytics (Idle)")
        self._btn_start.setEnabled(True)
        self._btn_stop.setEnabled(False)

    def _on_error(self, message: str) -> None:
        QMessageBox.critical(self, "Error", message)

    def closeEvent(self, event: QCloseEvent) -> None:
        if self._controller.running:
            self._controller.stop()
        event.accept()