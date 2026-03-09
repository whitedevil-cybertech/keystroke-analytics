"""Input capture subsystem — keyboard events and active window detection."""

from keystroke_analytics.capture.keyboard import KeyboardCapture
from keystroke_analytics.capture.window import ActiveWindowDetector

__all__ = ["KeyboardCapture", "ActiveWindowDetector"]
