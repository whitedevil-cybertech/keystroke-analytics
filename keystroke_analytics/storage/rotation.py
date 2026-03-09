"""
Size-based rotating file writer.

Opens a timestamped log file and automatically rotates to a new one
when the current file exceeds the configured size limit.  Thread-safe
via a lock around all write and rotation operations.
"""

import logging
from pathlib import Path
from datetime import datetime
from threading import Lock

logger = logging.getLogger(__name__)

_BYTES_PER_MB = 1024 * 1024


class RotatingFileWriter:
    """
    Writes text lines to rotating log files.

    Parameters:
        log_dir: Directory for log files (created if missing).
        prefix: Filename prefix for log files.
        max_size_mb: Rotate when the current file exceeds this size.
    """

    def __init__(
        self,
        log_dir: Path,
        prefix: str = "session",
        max_size_mb: float = 5.0,
    ) -> None:
        self._log_dir = log_dir
        self._prefix = prefix
        self._max_bytes = int(max_size_mb * _BYTES_PER_MB)
        self._lock = Lock()

        self._log_dir.mkdir(parents=True, exist_ok=True)
        self._current_path = self._new_path()
        self._file = open(self._current_path, "a", encoding="utf-8")

    @property
    def current_path(self) -> Path:
        """Path to the current log file."""
        return self._current_path

    def write(self, line: str) -> None:
        """Append a line to the log file and rotate if needed."""
        with self._lock:
            self._file.write(line + "\n")
            self._file.flush()
            self._maybe_rotate()

    def read_current(self) -> str:
        """Return the full content of the current log file."""
        with self._lock:
            self._file.flush()
            return self._current_path.read_text(encoding="utf-8")

    def close(self) -> None:
        """Flush and close the file handle."""
        with self._lock:
            self._file.close()

    # ------------------------------------------------------------------

    def _new_path(self) -> Path:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        return self._log_dir / f"{self._prefix}_{ts}.log"

    def _maybe_rotate(self) -> None:
        try:
            size = self._current_path.stat().st_size
        except FileNotFoundError:
            self._rotate()
            return
        if size >= self._max_bytes:
            self._rotate()

    def _rotate(self) -> None:
        self._file.close()
        self._current_path = self._new_path()
        self._file = open(self._current_path, "a", encoding="utf-8")
        logger.info("Rotated log to %s", self._current_path.name)
