"""Tests for keystroke_analytics.models."""

from datetime import datetime

from keystroke_analytics.models import InputEvent, SessionStats, KeyCategory


class TestKeyCategory:
    def test_all_members_exist(self):
        names = {m.name for m in KeyCategory}
        assert "ALPHA" in names
        assert "NUMERIC" in names
        assert "MODIFIER" in names
        assert "NAVIGATION" in names
        assert "PUNCTUATION" in names
        assert "WHITESPACE" in names
        assert "FUNCTION" in names
        assert "UNKNOWN" in names

    def test_values_are_unique(self):
        values = [m.value for m in KeyCategory]
        assert len(values) == len(set(values))


class TestInputEvent:
    def test_to_dict_all_fields(self):
        event = InputEvent(
            timestamp=datetime(2026, 1, 1, 12, 0, 0),
            key_label="a",
            category=KeyCategory.ALPHA,
            window_title="Terminal",
            dwell_ms=85.0,
            flight_ms=120.0,
        )
        d = event.to_dict()
        assert d["key"] == "a"
        assert d["category"] == "alpha"
        assert d["window"] == "Terminal"
        assert d["dwell_ms"] == 85.0
        assert d["flight_ms"] == 120.0
        assert "2026" in d["timestamp"]

    def test_to_dict_null_window(self):
        event = InputEvent(
            timestamp=datetime(2026, 1, 1),
            key_label="b",
        )
        assert event.to_dict()["window"] == "unknown"

    def test_to_log_line_with_window(self):
        event = InputEvent(
            timestamp=datetime(2026, 3, 15, 10, 30, 45),
            key_label="x",
            window_title="Firefox",
            dwell_ms=90.0,
        )
        line = event.to_log_line()
        assert "[Firefox]" in line
        assert "x" in line
        assert "dwell=90.0ms" in line
        assert "2026-03-15" in line

    def test_to_log_line_without_timing(self):
        event = InputEvent(
            timestamp=datetime(2026, 1, 1),
            key_label="y",
        )
        line = event.to_log_line()
        assert "y" in line
        assert "dwell=" not in line
        assert "flight=" not in line

    def test_to_log_line_with_flight(self):
        event = InputEvent(
            timestamp=datetime(2026, 1, 1),
            key_label="z",
            flight_ms=200.5,
        )
        line = event.to_log_line()
        assert "flight=200.5ms" in line


class TestSessionStats:
    def test_summary_contains_metrics(self):
        stats = SessionStats(
            duration_secs=30.0,
            total_keystrokes=150,
            words_per_minute=60.0,
            avg_dwell_ms=80.0,
            avg_flight_ms=130.0,
            rhythm_consistency=0.75,
            top_keys=[("e", 20), ("t", 15)],
            category_distribution={"alpha": 100, "whitespace": 50},
        )
        text = stats.summary()
        assert "30.0s" in text
        assert "150" in text
        assert "60.0 WPM" in text
        assert "80.0 ms" in text
        assert "0.75" in text
        assert "e" in text
        assert "alpha" in text

    def test_summary_empty_stats(self):
        stats = SessionStats()
        text = stats.summary()
        assert "TYPING ANALYTICS REPORT" in text
        assert "0.0s" in text
