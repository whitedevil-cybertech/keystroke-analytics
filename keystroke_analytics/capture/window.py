"""
Cross-platform active window title detection.

Supports Windows (win32gui + psutil), macOS (AppKit / NSWorkspace),
and Linux (xdotool).  Falls back gracefully when platform-specific
libraries are unavailable.
"""

import subprocess
import platform
import logging

logger = logging.getLogger(__name__)

_SYSTEM = platform.system()

# Lazy-loaded platform-specific modules.
_win32gui = None
_win32process = None
_psutil = None
_NSWorkspace = None

if _SYSTEM == "Windows":
    try:
        import win32gui as _win32gui  # type: ignore[no-redef]
        import win32process as _win32process  # type: ignore[no-redef]
        import psutil as _psutil  # type: ignore[no-redef]
    except ImportError:
        logger.debug("win32gui/psutil not available — window tracking disabled on Windows")

elif _SYSTEM == "Darwin":
    try:
        from AppKit import NSWorkspace as _NSWorkspace  # type: ignore[no-redef]
    except ImportError:
        logger.debug("AppKit not available — window tracking disabled on macOS")


class ActiveWindowDetector:
    """
    Detects the currently focused window title.

    Usage::

        detector = ActiveWindowDetector()
        title = detector.get_title()  # e.g. "Code.exe - main.py"
    """

    def get_title(self) -> str | None:
        """Return the active window title, or None if unavailable."""
        if _SYSTEM == "Windows":
            return self._windows_title()
        if _SYSTEM == "Darwin":
            return self._macos_title()
        if _SYSTEM == "Linux":
            return self._linux_title()
        return None

    # ------------------------------------------------------------------
    # Platform implementations
    # ------------------------------------------------------------------

    @staticmethod
    def _windows_title() -> str | None:
        if _win32gui is None:
            return None
        try:
            hwnd = _win32gui.GetForegroundWindow()
            _, pid = _win32process.GetWindowThreadProcessId(hwnd)
            process = _psutil.Process(pid)
            title = _win32gui.GetWindowText(hwnd)
            if title:
                return f"{process.name()} — {title}"
            return process.name()
        except Exception:
            return None

    @staticmethod
    def _macos_title() -> str | None:
        if _NSWorkspace is None:
            return None
        try:
            active = _NSWorkspace.sharedWorkspace().activeApplication()
            return active.get("NSApplicationName", "Unknown")
        except Exception:
            return None

    @staticmethod
    def _linux_title() -> str | None:
        try:
            result = subprocess.run(
                ["xdotool", "getactivewindow", "getwindowname"],
                capture_output=True,
                text=True,
                timeout=1,
                check=False,
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except FileNotFoundError:
            logger.debug("xdotool not installed — window tracking disabled on Linux")
        except Exception:
            pass
        return None
