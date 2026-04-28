"""
GUI entrypoint for keystroke analytics (PySide6).
"""

from __future__ import annotations

import logging
import signal
from pathlib import Path
from typing import Optional

from PySide6.QtWidgets import QApplication

from keystroke_analytics.gui.main_window import MainWindow

logger = logging.getLogger(__name__)


def run_gui(
    config_path: Optional[Path] = None,
    log_dir: Optional[Path] = None,
    encrypt: bool = False,
    analytics_enabled: bool = True,
) -> None:
    app = QApplication([])
    app.setApplicationName("Keystroke Analytics")
    app.setOrganizationName("keystroke-analytics")

    window = MainWindow(
        config_path=config_path,
        log_dir=log_dir,
        encrypt=encrypt,
        analytics_enabled=analytics_enabled,
    )
    window.show()
    logger.info("GUI launched")

    # Route Ctrl+C / SIGTERM to a clean shutdown.
    def _handle_signal(*_args: object) -> None:
        window.close()

    signal.signal(signal.SIGINT, _handle_signal)
    signal.signal(signal.SIGTERM, _handle_signal)

    app.exec()