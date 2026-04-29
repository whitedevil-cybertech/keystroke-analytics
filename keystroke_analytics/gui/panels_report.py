"""
Report viewer panel for displaying typing analytics reports and statistics.
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
    QTextEdit,
    QTabWidget,
    QMessageBox,
)

logger = logging.getLogger(__name__)


class ReportPanel(QWidget):
    """Panel for displaying typing analytics reports and session statistics."""

    def __init__(self) -> None:
        super().__init__()
        self._session_stats = None
        self._init_ui()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)

        # Title
        title = QLabel("Typing Analytics Report")
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title)

        # Create tab widget for different report views
        tabs = QTabWidget()

        # Summary tab
        summary_widget = self._create_summary_tab()
        tabs.addTab(summary_widget, "Summary")

        # Metrics tab
        metrics_widget = self._create_metrics_tab()
        tabs.addTab(metrics_widget, "Detailed Metrics")

        # Top keys tab
        topkeys_widget = self._create_topkeys_tab()
        tabs.addTab(topkeys_widget, "Key Frequency")

        layout.addWidget(tabs)

        # Action buttons
        action_layout = QHBoxLayout()

        btn_refresh = QPushButton("Refresh")
        btn_refresh.clicked.connect(self._refresh_report)
        action_layout.addWidget(btn_refresh)

        btn_export = QPushButton("Export Report")
        btn_export.clicked.connect(self._export_report)
        action_layout.addWidget(btn_export)

        action_layout.addStretch()
        layout.addLayout(action_layout)

    def _create_summary_tab(self) -> QWidget:
        """Create summary statistics tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        self._summary_text = QTextEdit()
        self._summary_text.setReadOnly(True)
        self._summary_text.setStyleSheet(
            "QTextEdit { font-family: 'Courier New', monospace; font-size: 10pt; background-color: #f5f5f5; }"
        )
        self._update_summary_text()
        layout.addWidget(self._summary_text)

        return widget

    def _create_metrics_tab(self) -> QWidget:
        """Create detailed metrics tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        self._metrics_text = QTextEdit()
        self._metrics_text.setReadOnly(True)
        self._metrics_text.setStyleSheet(
            "QTextEdit { font-family: 'Courier New', monospace; font-size: 9pt; background-color: #f5f5f5; }"
        )
        layout.addWidget(self._metrics_text)

        return widget

    def _create_topkeys_tab(self) -> QWidget:
        """Create top keys frequency tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        self._topkeys_text = QTextEdit()
        self._topkeys_text.setReadOnly(True)
        self._topkeys_text.setStyleSheet(
            "QTextEdit { font-family: 'Courier New', monospace; font-size: 9pt; background-color: #f5f5f5; }"
        )
        layout.addWidget(self._topkeys_text)

        return widget

    def _update_summary_text(self) -> None:
        """Update the summary tab with placeholder data."""
        summary = """
╔════════════════════════════════════════════════════╗
║       TYPING ANALYTICS REPORT - SUMMARY           ║
╚════════════════════════════════════════════════════╝

📊 SESSION OVERVIEW
─────────────────────────────────────────────────────

  Status              : No Active Session
  Duration            : -- seconds
  Total Keystrokes    : 0

⌨️  TYPING SPEED & TIMING
─────────────────────────────────────────────────────

  Words Per Minute    : -- WPM
  Avg Dwell Time      : -- ms (key hold duration)
  Avg Flight Time     : -- ms (key-to-key interval)
  Rhythm Consistency  : -- / 1.0

📈 KEY STATISTICS
─────────────────────────────────────────────────────

  Alphabet Keys       : 0
  Number Keys         : 0
  Special Keys        : 0
  Whitespace          : 0
  
🎯 TOP KEYS
─────────────────────────────────────────────────────

  • No data available

ℹ️  Notes:
  • Start a capture session to see live analytics
  • Report updates in real-time during capture
  • Session ends when you stop the capture
"""
        self._summary_text.setText(summary)

    def _refresh_report(self) -> None:
        """Refresh the report (placeholder)."""
        QMessageBox.information(self, "Info", "Report will auto-update during active capture")

    def _export_report(self) -> None:
        """Export the report to a file."""
        from PySide6.QtWidgets import QFileDialog

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Report", "", "Text Files (*.txt);;All Files (*)"
        )
        if file_path:
            try:
                with open(file_path, "w") as f:
                    f.write(self._summary_text.toPlainText())
                QMessageBox.information(self, "Success", f"Report exported to:\n{file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export report: {e}")
                logger.exception("Error exporting report")

    def update_report(self, session_stats: dict) -> None:
        """Update the report with new session statistics."""
        self._session_stats = session_stats

        # Generate summary
        duration = session_stats.get("duration", 0)
        total_keystrokes = session_stats.get("total_keystrokes", 0)
        wpm = session_stats.get("wpm", 0)
        avg_dwell = session_stats.get("avg_dwell_ms", 0)
        avg_flight = session_stats.get("avg_flight_ms", 0)
        rhythm_score = session_stats.get("rhythm_score", 0)

        summary = f"""
╔════════════════════════════════════════════════════╗
║       TYPING ANALYTICS REPORT - LIVE             ║
╚════════════════════════════════════════════════════╝

📊 SESSION OVERVIEW
─────────────────────────────────────────────────────

  Duration            : {duration:.1f} seconds
  Total Keystrokes    : {total_keystrokes}

⌨️  TYPING SPEED & TIMING
─────────────────────────────────────────────────────

  Words Per Minute    : {wpm:.1f} WPM
  Avg Dwell Time      : {avg_dwell:.1f} ms
  Avg Flight Time     : {avg_flight:.1f} ms
  Rhythm Consistency  : {rhythm_score:.2f} / 1.0

📈 KEY DISTRIBUTION
─────────────────────────────────────────────────────

  Alphabet Keys       : {session_stats.get("alpha_count", 0)}
  Number Keys         : {session_stats.get("numeric_count", 0)}
  Special Keys        : {session_stats.get("special_count", 0)}
  Whitespace          : {session_stats.get("whitespace_count", 0)}

🎯 TOP 10 KEYS
─────────────────────────────────────────────────────

"""
        top_keys = session_stats.get("top_keys", [])
        for i, (key, count) in enumerate(top_keys[:10], 1):
            bar_length = int(count / max([c for _, c in top_keys[:10]], 1) * 30)
            bar = "█" * bar_length
            summary += f"  {i:2d}. {key:15s} : {count:5d}  {bar}\n"

        summary += "\nℹ️  Report generated during active capture session."

        self._summary_text.setText(summary)

        # Update metrics tab
        metrics = f"""
DETAILED METRICS ANALYSIS
════════════════════════════════════════════════════════

Session Duration      : {duration:.2f} seconds
Total Events Recorded : {total_keystrokes}

TYPING DYNAMICS
─────────────────────────────────────────────────────
Words Per Minute (WPM)     : {wpm:.2f}
Average Dwell Time         : {avg_dwell:.2f} ms
Average Flight Time        : {avg_flight:.2f} ms
Rhythm Consistency Score   : {rhythm_score:.3f}

KEY FREQUENCY DISTRIBUTION
─────────────────────────────────────────────────────
Alphabetic Characters      : {session_stats.get("alpha_count", 0)}
Numeric Characters         : {session_stats.get("numeric_count", 0)}
Special/Punctuation        : {session_stats.get("special_count", 0)}
Whitespace (Space/Tab)     : {session_stats.get("whitespace_count", 0)}
Function/Control Keys      : {session_stats.get("function_count", 0)}

CALCULATION NOTES
─────────────────────────────────────────────────────
• WPM = (Character Count / 5) / (Duration in minutes)
• Dwell Time = Time key is held down (press to release)
• Flight Time = Time between consecutive key presses
• Rhythm Score = 1 / (1 + Coefficient of Variation)
  - Score close to 1.0 = Consistent typing rhythm
  - Score close to 0.0 = Erratic typing pattern
"""
        self._metrics_text.setText(metrics)

        # Update top keys tab
        topkeys_text = "TOP KEYS BY FREQUENCY\n" + "=" * 50 + "\n\n"
        for i, (key, count) in enumerate(top_keys, 1):
            topkeys_text += f"{i:2d}. {key:20s} {count:6d} times\n"

        self._topkeys_text.setText(topkeys_text)
