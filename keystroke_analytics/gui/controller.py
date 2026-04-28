"""
Controller for starting/stopping the analytics engine in a background thread.
"""

from __future__ import annotations

import logging
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from PySide6.QtCore import QObject, Signal

from keystroke_analytics.config import AppConfig
from keystroke_analytics.engine import AnalyticsEngine

logger = logging.getLogger(__name__)


@dataclass
class GuiConfigOverrides:
    config_path: Optional[Path]
    log_dir: Optional[Path]
    encrypt: bool
    analytics_enabled: bool
    passphrase: Optional[str]


class EngineController(QObject):
    started = Signal()
    stopped = Signal()
    error = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        self._thread: Optional[threading.Thread] = None
        self._engine: Optional[AnalyticsEngine] = None
        self._running = False

    @property
    def running(self) -> bool:
        return self._running

    def start(self, overrides: GuiConfigOverrides) -> None:
        if self._running:
            return

        try:
            if overrides.config_path and overrides.config_path.exists():
                config = AppConfig.from_file(overrides.config_path)
            else:
                config = AppConfig()

            if overrides.log_dir:
                config.storage.log_dir = overrides.log_dir
            if overrides.encrypt:
                config.storage.encrypt = True
                config.storage.passphrase = overrides.passphrase
            if not overrides.analytics_enabled:
                config.analytics.enabled = False

            if config.storage.encrypt and not config.storage.passphrase:
                raise ValueError("Encryption enabled but no passphrase provided.")

            self._engine = AnalyticsEngine(config)

            self._thread = threading.Thread(target=self._engine.start, daemon=True)
            self._thread.start()

            self._running = True
            self.started.emit()
            logger.info("Capture started (GUI)")
        except Exception as exc:  # noqa: BLE001
            logger.exception("Failed to start engine")
            self.error.emit(str(exc))

    def stop(self) -> None:
        if not self._running or not self._engine:
            return
        try:
            self._engine.stop()
            self._running = False
            self.stopped.emit()
            logger.info("Capture stopped (GUI)")
        except Exception as exc:  # noqa: BLE001
            logger.exception("Failed to stop engine")
            self.error.emit(str(exc))