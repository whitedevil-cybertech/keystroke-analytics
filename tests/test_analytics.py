"""Tests for keystroke_analytics.analytics.biometrics."""

from datetime import datetime, timedelta

from keystroke_analytics.models import InputEvent, KeyCategory
from keystroke_analytics.analytics.biometrics import TypingBiometrics, _safe_mean


class TestSafeMean:
    def test_empty(self):
        assert _safe_mean([]) == 0.0

    def test_single(self):
        assert _safe_mean([10.0]) == 10.0

    def test_multiple(self):
        assert _safe_mean([10.0, 20.0, 30.0]) == 20.0


class TestTypingBiometrics:
    def _make_event(self, key, category=KeyCategory.ALPHA, offset_secs=0,
                    dwell_ms=None, flight_ms=None):
        return InputEvent(
            timestamp=datetime(2026, 1, 1) + timedelta(seconds=offset_secs),
            key_label=key,
            category=category,
            dwell_ms=dwell_ms,
            flight_ms=flight_ms,
        )

    def test_empty_report(self):
        bio = TypingBiometrics()
        stats = bio.report()
        assert stats.total_keystrokes == 0
        assert stats.words_per_minute == 0.0
        assert stats.rhythm_consistency == 0.0

    def test_keystroke_counting(self):
        bio = TypingBiometrics()
        for i, ch in enumerate("hello"):
            bio.record_event(self._make_event(ch, offset_secs=i * 0.2))
        stats = bio.report()
        assert stats.total_keystrokes == 5

    def test_wpm_calculation(self):
        bio = TypingBiometrics()
        # 25 alpha characters over 60 seconds = 5 words/min
        for i in range(25):
            bio.record_event(self._make_event(
                "a", offset_secs=i * 2.4,  # spread over 60s
            ))
        stats = bio.report()
        assert 4.0 <= stats.words_per_minute <= 6.0

    def test_key_frequency(self):
        bio = TypingBiometrics()
        for _ in range(10):
            bio.record_event(self._make_event("e"))
        for _ in range(3):
            bio.record_event(self._make_event("x"))
        stats = bio.report()
        # top_keys should have 'e' first
        assert stats.top_keys[0] == ("e", 10)

    def test_category_distribution(self):
        bio = TypingBiometrics()
        bio.record_event(self._make_event("a", KeyCategory.ALPHA))
        bio.record_event(self._make_event("[SPACE]", KeyCategory.WHITESPACE))
        bio.record_event(self._make_event("[SHIFT]", KeyCategory.MODIFIER))
        stats = bio.report()
        assert "alpha" in stats.category_distribution
        assert "whitespace" in stats.category_distribution
        assert "modifier" in stats.category_distribution

    def test_dwell_averaging(self):
        bio = TypingBiometrics()
        bio.record_event(self._make_event("a", dwell_ms=100.0))
        bio.record_event(self._make_event("b", dwell_ms=200.0))
        stats = bio.report()
        assert stats.avg_dwell_ms == 150.0

    def test_flight_averaging(self):
        bio = TypingBiometrics()
        bio.record_event(self._make_event("a", flight_ms=100.0))
        bio.record_event(self._make_event("b", flight_ms=200.0))
        stats = bio.report()
        assert stats.avg_flight_ms == 150.0

    def test_rhythm_consistency_even_cadence(self):
        """Perfectly even flight times should score close to 1.0."""
        bio = TypingBiometrics()
        for i in range(20):
            bio.record_event(self._make_event(
                "a", offset_secs=i * 0.2, flight_ms=200.0,
            ))
        stats = bio.report()
        assert stats.rhythm_consistency >= 0.95

    def test_rhythm_consistency_erratic(self):
        """Wildly varying flight times should score low."""
        bio = TypingBiometrics()
        flights = [50.0, 500.0, 30.0, 800.0, 100.0, 1000.0, 40.0, 600.0]
        for i, f in enumerate(flights):
            bio.record_event(self._make_event("a", offset_secs=i, flight_ms=f))
        stats = bio.report()
        assert stats.rhythm_consistency < 0.5

    def test_update_dwell_retroactive(self):
        bio = TypingBiometrics()
        bio.record_event(self._make_event("a"))  # no dwell_ms yet
        bio.update_dwell("a", 95.0)
        stats = bio.report()
        assert stats.avg_dwell_ms == 95.0

    def test_modifiers_not_counted_for_wpm(self):
        """Modifier keys shouldn't inflate WPM."""
        bio = TypingBiometrics()
        for i in range(10):
            bio.record_event(self._make_event(
                "[SHIFT]", KeyCategory.MODIFIER, offset_secs=i,
            ))
        stats = bio.report()
        assert stats.words_per_minute == 0.0
