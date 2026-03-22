"""
Typing biometrics analyzer.

Computes keystroke-dynamics metrics from a stream of ``InputEvent`` objects:

* **Words per minute (WPM)** — estimated from character-key presses using
  the standard 5-characters-per-word convention.
* **Dwell time** — how long each key is held down (press→release).
* **Flight time** — the gap between consecutive key presses.
* **Rhythm consistency** — a 0–1 score derived from the coefficient of
  variation of flight times; a perfectly even cadence scores 1.0.
* **Key frequency distribution** — counts per key label.
* **Category distribution** — counts per ``KeyCategory``.

These metrics form a *keystroke-dynamics profile* that can be used for
behavioural biometric authentication or productivity analysis.
"""

import math
import logging
from collections import Counter
from threading import Lock

from keystroke_analytics.models import InputEvent, SessionStats, KeyCategory

logger = logging.getLogger(__name__)


class TypingBiometrics:
    """
    Accumulates keystroke events and produces a ``SessionStats`` report.

    Thread-safe: ``record_event`` can be called from the capture thread
    while ``report`` is called from the main thread.
    """

    def __init__(self) -> None:
        self._lock = Lock()
        self._events: list[InputEvent] = []
        self._dwell_values: list[float] = []
        self._flight_values: list[float] = []
        self._key_counts: Counter[str] = Counter()
        self._category_counts: Counter[str] = Counter()
        self._char_count: int = 0
        self._start_time: float | None = None  # epoch seconds
        self._end_time: float | None = None

    # ------------------------------------------------------------------
    # Recording
    # ------------------------------------------------------------------

    def record_event(self, event: InputEvent) -> None:
        """Feed a new keystroke event into the analyzer."""
        ts = event.timestamp.timestamp()

        with self._lock:
            if self._start_time is None:
                self._start_time = ts
            self._end_time = ts

            self._events.append(event)
            self._key_counts[event.key_label] += 1
            self._category_counts[event.category.name.lower()] += 1

            if event.dwell_ms is not None:
                self._dwell_values.append(event.dwell_ms)
            if event.flight_ms is not None:
                self._flight_values.append(event.flight_ms)

            # Count character keys for WPM calculation.
            if event.category in (KeyCategory.ALPHA, KeyCategory.NUMERIC,
                                  KeyCategory.PUNCTUATION, KeyCategory.WHITESPACE):
                self._char_count += 1

    def update_dwell(self, key_label: str, dwell_ms: float) -> None:
        """
        Retroactively attach dwell time to the most recent event for *key_label*.

        Called by the engine when a key-release arrives after the press
        event has already been recorded.
        """
        with self._lock:
            # Walk backwards to find the matching event.
            for evt in reversed(self._events):
                if evt.key_label == key_label and evt.dwell_ms is None:
                    evt.dwell_ms = dwell_ms
                    self._dwell_values.append(dwell_ms)
                    break

    # ------------------------------------------------------------------
    # Reporting
    # ------------------------------------------------------------------

    def report(self) -> SessionStats:
        """Compute and return a ``SessionStats`` snapshot."""
        with self._lock:
            duration = 0.0
            if self._start_time is not None and self._end_time is not None:
                duration = max(self._end_time - self._start_time, 0.001)

            total = len(self._events)
            wpm = self._compute_wpm(duration)
            avg_dwell = _safe_mean(self._dwell_values)
            avg_flight = _safe_mean(self._flight_values)
            rhythm = self._rhythm_score()

            top_keys = self._key_counts.most_common(10)
            categories = dict(self._category_counts)

        return SessionStats(
            duration_secs=round(duration, 2),
            total_keystrokes=total,
            words_per_minute=round(wpm, 1),
            avg_dwell_ms=round(avg_dwell, 1),
            avg_flight_ms=round(avg_flight, 1),
            top_keys=top_keys,
            category_distribution=categories,
            rhythm_consistency=round(rhythm, 3),
        )

    # ------------------------------------------------------------------
    # Internal calculations
    # ------------------------------------------------------------------

    def _compute_wpm(self, duration_secs: float) -> float:
        """Estimate words per minute (5 chars = 1 word)."""
        if duration_secs <= 0:
            return 0.0
        words = self._char_count / 5.0
        minutes = duration_secs / 60.0
        return words / minutes if minutes > 0 else 0.0

    def _rhythm_score(self) -> float:
        """
        Compute rhythm consistency from flight-time variance.

        Uses ``1 / (1 + CV)`` where CV is the coefficient of variation
        (std_dev / mean) of flight times.  A perfectly even cadence
        yields CV ≈ 0 → score ≈ 1.0.  Highly erratic typing yields
        large CV → score → 0.
        """
        if len(self._flight_values) < 2:
            return 0.0

        mean = _safe_mean(self._flight_values)
        if mean <= 0:
            return 0.0

        variance = sum((v - mean) ** 2 for v in self._flight_values) / len(self._flight_values)
        std_dev = math.sqrt(variance)
        cv = std_dev / mean

        return 1.0 / (1.0 + cv)


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

def _safe_mean(values: list[float]) -> float:
    """Return the arithmetic mean, or 0.0 for an empty list."""
    if not values:
        return 0.0
    return sum(values) / len(values)
