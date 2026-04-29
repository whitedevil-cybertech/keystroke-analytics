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
    QGridLayout,
    QWidget,
    QLabel,
    QPushButton,
    QCheckBox,
    QFrame,
    QLineEdit,
    QMessageBox,
)

from .widgets import CustomButton, MetricCard, ICONS
from .theme import Theme

logger = logging.getLogger(__name__)


class StatsPanel(QWidget):
    """Panel for displaying real-time statistics and configuration."""

    def __init__(self) -> None:
        super().__init__()
        self._init_ui()

    def _init_ui(self) -> None:
        self._enc_checkbox = QCheckBox("🔒 AES Encryption")
        self._analytics_checkbox = QCheckBox("📊 Biometrics Analysis")
        self._analytics_checkbox.setChecked(True)
        self._window_checkbox = QCheckBox("🪟 Window Tracking")
        self._special_checkbox = QCheckBox("⌨️ Special Keys")
        self._log_dir_input = QLineEdit()
        self._log_dir_input.setReadOnly(True)

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(24)
        main_layout.setContentsMargins(32, 32, 32, 32)

        # Header
        header = QLabel("📊 Live Analytics Dashboard")
        header.setProperty("role", "title")
        main_layout.addWidget(header)

        # Metrics grid - dashboard cards
        metrics_frame = QFrame()
        metrics_frame.setProperty("role", "card")
        metrics_layout = QGridLayout(metrics_frame)
        metrics_layout.setSpacing(20)

        # Define metrics with icons and colors
        self._metric_cards = {}
        metrics_config = [
            (ICONS.get('time', '⏱️'), "00:00", "Elapsed", "#00d4aa"),
            (ICONS.get('key', '⌨️'), "0", "Keystrokes", "#2ed573"),
            ("⚡", "0.0", "WPM", "#ffb300"),
            ("⏱️", "0ms", "Avg Dwell", "#ff6b6b"),
            ("✈️", "0ms", "Avg Flight", "#747d8c"),
            ("🎵", "0.00", "Rhythm", "#00d4aa"),
            ("🔑", "N/A", "Top Key", "#2ed573"),
        ]

        row, col = 0, 0
        for icon, value, subtitle, color in metrics_config:
            card = MetricCard(icon, value, subtitle, color)
            self._metric_cards[subtitle.lower().replace(' ', '_')] = card
            metrics_layout.addWidget(card, row, col)
            col += 1
            if col == 3:
                col = 0
                row += 1

        main_layout.addWidget(metrics_frame)

        # Settings card (modern replacement for groupboxes)
        settings_frame = QFrame()
        settings_frame.setProperty("role", "card")
        settings_layout = QVBoxLayout(settings_frame)
        settings_layout.setSpacing(16)

        settings_title = QLabel("⚙️ Capture Preferences")
        settings_title.setProperty("role", "title")
        settings_layout.addWidget(settings_title)

        # Modern toggles
        toggles = [
            ("🔒 AES Encryption", self._enc_checkbox if hasattr(self, '_enc_checkbox') else None),
            ("📊 Biometrics", self._analytics_checkbox if hasattr(self, '_analytics_checkbox') else None),
            ("🪟 Window Tracking", self._window_checkbox if hasattr(self, '_window_checkbox') else None),
            ("⌨️ Special Keys", self._special_checkbox if hasattr(self, '_special_checkbox') else None),
        ]

        for text, checkbox in toggles:
            if checkbox:
                toggle_layout = QHBoxLayout()
                toggle_layout.addWidget(checkbox)
                toggle_layout.addStretch()
                settings_layout.addLayout(toggle_layout)

        main_layout.addWidget(settings_frame)

        # Action buttons (styled)
        action_layout = QHBoxLayout()
        action_layout.addStretch()
        btn_save = CustomButton("💾 Save Preferences", role="secondary")
        btn_save.clicked.connect(self._save_settings)
        action_layout.addWidget(btn_save)

        btn_reset = CustomButton("🔄 Reset", role="secondary")
        btn_reset.clicked.connect(self._reset_defaults)
        action_layout.addWidget(btn_reset)

        main_layout.addLayout(action_layout)

        main_layout.addStretch()

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
        """Update metric cards with live data."""
        # Elapsed time formatting
        elapsed = stats.get('elapsed_time', 0)
        minutes = int(elapsed // 60)
        seconds = int(elapsed % 60)
        self._metric_cards['elapsed'].setValue(f"{minutes:02d}:{seconds:02d}")

        # Metric cards
        self._metric_cards['keystrokes'].setValue(f"{int(stats.get('keystrokes', 0)):,}")
        self._metric_cards['wpm'].setValue(f"{stats.get('wpm', 0):.1f}")
        self._metric_cards['avg_dwell'].setValue(f"{stats.get('avg_dwell_ms', 0):.0f}ms")
        self._metric_cards['avg_flight'].setValue(f"{stats.get('avg_flight_ms', 0):.0f}ms")
        self._metric_cards['rhythm'].setValue(f"{stats.get('rhythm_score', 0):.2f}")
        self._metric_cards['top_key'].setValue(stats.get('top_key', 'N/A') or 'N/A')

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
