"""
Statistics panel for displaying real-time analytics and session info.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QLabel,
    QPushButton,
    QLineEdit,
    QCheckBox,
    QGroupBox,
    QMessageBox,
    QSpinBox,
    QComboBox,
)

logger = logging.getLogger(__name__)


class StatsPanel(QWidget):
    """Panel for displaying real-time statistics and configuration."""

    def __init__(self) -> None:
        super().__init__()
        self._init_ui()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)

        # Title
        title = QLabel("Session Statistics & Settings")
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title)

        # Real-time stats group
        stats_group = QGroupBox("Real-Time Statistics")
        stats_layout = QVBoxLayout()

        # Create stat rows
        self._stats = {}
        stat_labels = [
            ("Elapsed Time", "elapsed_time", "0s"),
            ("Keystrokes Captured", "keystrokes", "0"),
            ("Current WPM", "wpm", "0.0"),
            ("Avg Dwell Time", "dwell", "0.0 ms"),
            ("Avg Flight Time", "flight", "0.0 ms"),
            ("Rhythm Score", "rhythm", "0.0 / 1.0"),
            ("Top Key", "top_key", "N/A"),
            ("Session Status", "status", "Idle"),
        ]

        for label_text, key, default_value in stat_labels:
            row_layout = QHBoxLayout()
            label = QLabel(f"{label_text}:")
            label.setMinimumWidth(150)
            value = QLineEdit(default_value)
            value.setReadOnly(True)
            value.setStyleSheet(
                "QLineEdit { background-color: #f0f0f0; border: 1px solid #ddd; }"
            )
            row_layout.addWidget(label)
            row_layout.addWidget(value)
            stats_layout.addLayout(row_layout)
            self._stats[key] = value

        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)

        # Settings group
        settings_group = QGroupBox("Capture Settings")
        settings_layout = QVBoxLayout()

        # Log directory
        logdir_layout = QHBoxLayout()
        logdir_layout.addWidget(QLabel("Log Directory:"))
        self._log_dir_input = QLineEdit()
        self._log_dir_input.setReadOnly(True)
        logdir_layout.addWidget(self._log_dir_input)
        settings_layout.addLayout(logdir_layout)

        # Encryption
        enc_layout = QHBoxLayout()
        self._enc_checkbox = QCheckBox("Enable Encryption (AES-128)")
        enc_layout.addWidget(self._enc_checkbox)
        enc_layout.addStretch()
        settings_layout.addLayout(enc_layout)

        # Analytics
        analytics_layout = QHBoxLayout()
        self._analytics_checkbox = QCheckBox("Enable Biometrics Analysis")
        self._analytics_checkbox.setChecked(True)
        analytics_layout.addWidget(self._analytics_checkbox)
        analytics_layout.addStretch()
        settings_layout.addLayout(analytics_layout)

        # Window tracking
        window_layout = QHBoxLayout()
        self._window_checkbox = QCheckBox("Track Active Window")
        window_layout.addWidget(self._window_checkbox)
        window_layout.addStretch()
        settings_layout.addLayout(window_layout)

        # Special keys logging
        special_layout = QHBoxLayout()
        self._special_checkbox = QCheckBox("Log Special Keys (Ctrl, Alt, etc.)")
        special_layout.addWidget(self._special_checkbox)
        special_layout.addStretch()
        settings_layout.addLayout(special_layout)

        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)

        # Action buttons
        action_layout = QHBoxLayout()
        btn_save = QPushButton("Save Settings")
        btn_save.clicked.connect(self._save_settings)
        action_layout.addWidget(btn_save)

        btn_reset = QPushButton("Reset to Defaults")
        btn_reset.clicked.connect(self._reset_defaults)
        action_layout.addWidget(btn_reset)

        action_layout.addStretch()
        layout.addLayout(action_layout)

        layout.addStretch()

    def _save_settings(self) -> None:
        """Save the current settings."""
        QMessageBox.information(
            self,
            "Settings",
            "Settings saved! These will apply to the next capture session.",
        )

    def _reset_defaults(self) -> None:
        """Reset settings to defaults."""
        self._enc_checkbox.setChecked(False)
        self._analytics_checkbox.setChecked(True)
        self._window_checkbox.setChecked(False)
        self._special_checkbox.setChecked(True)
        QMessageBox.information(self, "Reset", "Settings reset to defaults.")

    def update_stats(self, stats: dict) -> None:
        """Update statistics display with new data."""
        for key, field in [
            ("elapsed_time", "elapsed_time"),
            ("keystrokes", "keystrokes"),
            ("wpm", "wpm"),
            ("dwell", "avg_dwell_ms"),
            ("flight", "avg_flight_ms"),
            ("rhythm", "rhythm_score"),
            ("top_key", "top_key"),
            ("status", "status"),
        ]:
            if key in self._stats:
                value = stats.get(field, "N/A")
                if key == "wpm":
                    self._stats[key].setText(f"{value:.1f}")
                elif key in ["dwell", "flight"]:
                    self._stats[key].setText(f"{value:.1f} ms" if value != "N/A" else "N/A")
                elif key == "rhythm":
                    self._stats[key].setText(
                        f"{value:.2f} / 1.0" if value != "N/A" else "N/A"
                    )
                elif key == "elapsed_time":
                    self._stats[key].setText(f"{value:.1f}s" if value != "N/A" else "N/A")
                else:
                    self._stats[key].setText(str(value))

    def set_log_directory(self, log_dir: Optional[Path]) -> None:
        """Set the log directory display."""
        if log_dir:
            self._log_dir_input.setText(str(log_dir))
        else:
            self._log_dir_input.setText(str(Path.home() / ".keystroke_analytics"))

    def get_settings(self) -> dict:
        """Get current settings."""
        return {
            "encrypt": self._enc_checkbox.isChecked(),
            "analytics": self._analytics_checkbox.isChecked(),
            "track_windows": self._window_checkbox.isChecked(),
            "log_special": self._special_checkbox.isChecked(),
        }
