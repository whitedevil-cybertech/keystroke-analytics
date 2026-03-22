"""
Keystroke Analytics — Cross-platform input analytics with typing biometrics.

A modular toolkit for capturing keyboard events, computing keystroke-dynamics
metrics (WPM, dwell time, flight time, rhythm consistency), and storing
results with optional AES encryption.
"""

__version__ = "1.0.0"

from keystroke_analytics.models import InputEvent, SessionStats, KeyCategory
from keystroke_analytics.config import AppConfig
from keystroke_analytics.engine import AnalyticsEngine

__all__ = [
    "InputEvent",
    "SessionStats",
    "KeyCategory",
    "AppConfig",
    "AnalyticsEngine",
]
