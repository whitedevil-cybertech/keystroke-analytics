"""
Main GUI window with tabbed interface for capture, logs, and reports.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

from PySide6.QtCore import QTimer
from PySide6.QtGui import QCloseEvent, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QDialog,
    QFileDialog,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QTabWidget,
)

from keystroke_analytics.gui.controller import EngineController, GuiConfigOverrides
from keystroke_analytics.gui.dialogs import ConsentDialog, PassphraseDialog
from keystroke_analytics.gui.panels_logs import LogsPanel
from keystroke_analytics.gui.panels_report import ReportPanel
from keystroke_analytics.gui.panels_stats import StatsPanel

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
        self.setWindowTitle("Keystroke Analytics - Enhanced GUI")
        self.setGeometry(100, 100, 1200, 800)

        self._config_path = config_path
        self._log_dir = log_dir
        self._encrypt = encrypt
        self._analytics_enabled = analytics_enabled

        self._controller = EngineController()
        self._controller.started.connect(self._on_started)
        self._controller.stopped.connect(self._on_stopped)
        self._controller.error.connect(self._on_error)
        self._controller.stats_updated.connect(self._on_stats_updated)

        # Create main widget and layout
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)

        # Top control panel
        control_layout = QHBoxLayout()
        self._status = QLabel("Status: Idle")
        self._status.setStyleSheet("font-weight: bold; font-size: 12px;")
        control_layout.addWidget(self._status)

        self._btn_start = QPushButton("▶ Start Capture")
        self._btn_stop = QPushButton("⏹ Stop Capture")
        self._btn_stop.setEnabled(False)
        self._btn_choose_log = QPushButton("📁 Choose Log Directory")

        self._btn_start.clicked.connect(self._start_clicked)
        self._btn_stop.clicked.connect(self._stop_clicked)
        self._btn_choose_log.clicked.connect(self._choose_log_dir)

        control_layout.addWidget(self._btn_choose_log)
        control_layout.addWidget(self._btn_start)
        control_layout.addWidget(self._btn_stop)
        control_layout.addStretch()

        main_layout.addLayout(control_layout)

        # Tabbed interface
        self._tabs = QTabWidget()

        # Capture tab
        self._capture_tab = self._create_capture_tab()
        self._tabs.addTab(self._capture_tab, "📊 Capture & Control")

        # Statistics tab
        self._stats_panel = StatsPanel()
        self._stats_panel.set_log_directory(log_dir)
        self._tabs.addTab(self._stats_panel, "📈 Statistics")

        # Report tab
        self._report_panel = ReportPanel()
        self._tabs.addTab(self._report_panel, "📋 Report")

        # Logs tab
        self._logs_panel = LogsPanel()
        self._logs_panel.set_log_directory(log_dir)
        self._tabs.addTab(self._logs_panel, "📄 Logs Viewer")

        main_layout.addWidget(self._tabs)

        self.setCentralWidget(main_widget)

        # Panic stop shortcut: Ctrl+Shift+Q
        self._panic = QShortcut(QKeySequence("Ctrl+Shift+Q"), self)
        self._panic.activated.connect(self._stop_clicked)

        # Timer for periodic refresh
        self._refresh_timer = QTimer()
        self._refresh_timer.timeout.connect(self._refresh_panels)

    def _create_capture_tab(self) -> QWidget:
        """Create the main capture control tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        title = QLabel("Keystroke Capture Control")
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title)

        info_layout = QVBoxLayout()
        self._log_dir_label = QLabel(f"Log Directory: {self._log_dir or 'default'}")
        self._enc_label = QLabel(f"Encryption: {'🔒 ENABLED' if self._encrypt else '🔓 Disabled'}")
        self._analytics_label = QLabel(
            f"Analytics: {'✓ Enabled' if self._analytics_enabled else '✗ Disabled'}"
        )

        info_layout.addWidget(self._log_dir_label)
        info_layout.addWidget(self._enc_label)
        info_layout.addWidget(self._analytics_label)

        layout.addLayout(info_layout)

        # Instructions
        instructions = QLabel(
            "Instructions:\n"
            "1. Choose a log directory (optional)\n"
            "2. Click 'Start Capture' to begin recording keystrokes\n"
            "3. Your typing metrics will update in real-time in the 'Statistics' tab\n"
            "4. View detailed reports in the 'Report' tab\n"
            "5. Access raw logs in the 'Logs Viewer' tab\n"
            "6. Press Ctrl+Shift+Q to emergency stop\n\n"
            "⚠️  Disclaimer: This tool captures keystrokes. Only use with explicit authorization."
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet(
            "QLabel { background-color: #fffacd; padding: 10px; border-radius: 5px; }"
        )
        layout.addWidget(instructions)

        layout.addStretch()

        # Quick stats
        stats_box = QLabel(
            "Quick Stats:\n"
            "• Monitor WPM (Words Per Minute)\n"
            "• Track typing consistency (Rhythm Score)\n"
            "• Analyze key frequency patterns\n"
            "• Export reports for analysis"
        )
        stats_box.setStyleSheet(
            "QLabel { background-color: #e6f3ff; padding: 10px; border-radius: 5px; }"
        )
        layout.addWidget(stats_box)

        return widget

    def _choose_log_dir(self) -> None:
        directory = QFileDialog.getExistingDirectory(self, "Select Log Directory")
        if directory:
            self._log_dir = Path(directory)
            self._log_dir_label.setText(f"Log Directory: {self._log_dir}")
            self._stats_panel.set_log_directory(self._log_dir)
            self._logs_panel.set_log_directory(self._log_dir)

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
        self._refresh_timer.start(1000)  # Update every second

    def _stop_clicked(self) -> None:
        self._controller.stop()
        self._refresh_timer.stop()

    def _on_started(self) -> None:
        self._status.setText("✓ Status: Recording")
        self._status.setStyleSheet("font-weight: bold; font-size: 12px; color: green;")
        self.setWindowTitle("Keystroke Analytics - Recording...")
        self._btn_start.setEnabled(False)
        self._btn_stop.setEnabled(True)

    def _on_stopped(self) -> None:
        self._status.setText("✗ Status: Idle")
        self._status.setStyleSheet("font-weight: bold; font-size: 12px; color: red;")
        self.setWindowTitle("Keystroke Analytics - Idle")
        self._btn_start.setEnabled(True)
        self._btn_stop.setEnabled(False)
        self._refresh_timer.stop()
        self._logs_panel.set_log_directory(self._log_dir)

    def _on_error(self, message: str) -> None:
        QMessageBox.critical(self, "Error", message)

    def _on_stats_updated(self, stats: dict) -> None:
        """Handle stats update signal from controller."""
        self._stats_panel.update_stats(stats)
        self._report_panel.update_report(stats)

    def _refresh_panels(self) -> None:
        """Periodic refresh of panels during capture."""
        self._logs_panel.set_log_directory(self._log_dir)

    def closeEvent(self, event: QCloseEvent) -> None:
        if self._controller.running:
            self._controller.stop()
        event.accept()