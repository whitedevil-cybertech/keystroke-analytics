"""
Logs viewer panel for displaying captured keystroke logs.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QTextEdit,
    QPushButton,
    QLineEdit,
    QLabel,
    QFileDialog,
    QMessageBox,
)

logger = logging.getLogger(__name__)


class LogsPanel(QWidget):
    """Panel for viewing and managing keystroke logs."""

    def __init__(self) -> None:
        super().__init__()
        self._current_log_file: Optional[Path] = None
        self._init_ui()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)

        # Title
        title = QLabel("Keystroke Logs Viewer")
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title)

        # File selection row
        file_layout = QHBoxLayout()
        file_layout.addWidget(QLabel("Log File:"))
        self._file_path = QLineEdit()
        self._file_path.setReadOnly(True)
        file_layout.addWidget(self._file_path)

        btn_browse = QPushButton("Browse...")
        btn_browse.clicked.connect(self._browse_logs)
        file_layout.addWidget(btn_browse)

        btn_open_dir = QPushButton("Open Directory")
        btn_open_dir.clicked.connect(self._open_log_directory)
        file_layout.addWidget(btn_open_dir)

        layout.addLayout(file_layout)

        # Search row
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Search:"))
        self._search_input = QLineEdit()
        self._search_input.setPlaceholderText("Enter text to search in logs...")
        self._search_input.textChanged.connect(self._filter_logs)
        search_layout.addWidget(self._search_input)

        btn_clear_search = QPushButton("Clear")
        btn_clear_search.clicked.connect(self._clear_search)
        search_layout.addWidget(btn_clear_search)

        layout.addLayout(search_layout)

        # Text display
        self._text_display = QTextEdit()
        self._text_display.setReadOnly(True)
        self._text_display.setStyleSheet(
            "QTextEdit { font-family: 'Courier New', monospace; font-size: 9pt; }"
        )
        layout.addWidget(self._text_display)

        # Action buttons
        action_layout = QHBoxLayout()
        btn_reload = QPushButton("Reload")
        btn_reload.clicked.connect(self._reload_logs)
        action_layout.addWidget(btn_reload)

        btn_copy = QPushButton("Copy All")
        btn_copy.clicked.connect(self._copy_logs)
        action_layout.addWidget(btn_copy)

        action_layout.addStretch()
        layout.addLayout(action_layout)

    def _browse_logs(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Log File", "", "Log Files (*.log *.enc *.txt);;All Files (*)"
        )
        if file_path:
            self._current_log_file = Path(file_path)
            self._file_path.setText(str(self._current_log_file))
            self._load_log_file()

    def _open_log_directory(self) -> None:
        log_dir = Path.home() / ".keystroke_analytics"
        if not log_dir.exists():
            QMessageBox.information(self, "No Logs", f"Log directory not found: {log_dir}")
            return

        import subprocess
        import sys

        try:
            if sys.platform == "win32":
                subprocess.Popen(f'explorer "{log_dir}"')
            elif sys.platform == "darwin":
                subprocess.Popen(["open", str(log_dir)])
            else:
                subprocess.Popen(["xdg-open", str(log_dir)])
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open directory: {e}")

    def _load_log_file(self) -> None:
        if not self._current_log_file or not self._current_log_file.exists():
            QMessageBox.warning(self, "Error", "Log file not found or not selected")
            return

        try:
            content = self._current_log_file.read_text(encoding="utf-8", errors="ignore")
            self._text_display.setText(content)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to read log file: {e}")
            logger.exception("Error reading log file")

    def _filter_logs(self) -> None:
        if not self._current_log_file:
            return

        try:
            content = self._current_log_file.read_text(encoding="utf-8", errors="ignore")
            search_term = self._search_input.text().lower()

            if search_term:
                lines = content.split("\n")
                filtered_lines = [line for line in lines if search_term in line.lower()]
                self._text_display.setText(
                    f"[{len(filtered_lines)} matches found]\n\n" + "\n".join(filtered_lines)
                )
            else:
                self._text_display.setText(content)
        except Exception as e:
            logger.exception("Error filtering logs")

    def _clear_search(self) -> None:
        self._search_input.clear()

    def _reload_logs(self) -> None:
        if self._current_log_file:
            self._load_log_file()

    def _copy_logs(self) -> None:
        from PySide6.QtWidgets import QApplication

        clipboard = QApplication.clipboard()
        clipboard.setText(self._text_display.toPlainText())
        QMessageBox.information(self, "Success", "Logs copied to clipboard")

    def set_log_directory(self, log_dir: Optional[Path]) -> None:
        """Set the default log directory."""
        if log_dir and log_dir.exists():
            log_files = list(log_dir.glob("*.log")) + list(log_dir.glob("*.enc"))
            if log_files:
                # Load the most recent log file
                latest_log = max(log_files, key=lambda p: p.stat().st_mtime)
                self._current_log_file = latest_log
                self._file_path.setText(str(self._current_log_file))
                self._load_log_file()
