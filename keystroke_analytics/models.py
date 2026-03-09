"""
Data models for keystroke analytics.

Defines the core data structures used throughout the application:
InputEvent captures individual keystrokes with timing data for biometric
analysis, SessionStats aggregates typing metrics over a capture session,
and KeyCategory classifies keys for frequency analysis.
"""

from enum import Enum, auto
from dataclasses import dataclass, field
from datetime import datetime


class KeyCategory(Enum):
    """Classifies a keystroke for analytics grouping."""

    ALPHA = auto()
    NUMERIC = auto()
    MODIFIER = auto()
    NAVIGATION = auto()
    PUNCTUATION = auto()
    WHITESPACE = auto()
    FUNCTION = auto()
    UNKNOWN = auto()


@dataclass
class InputEvent:
    """
    A single keystroke with timing and context.

    Attributes:
        timestamp: When the key was pressed.
        key_label: Human-readable key name (e.g. 'a', '[ENTER]').
        category: Classification of the key.
        window_title: Active window at time of capture.
        dwell_ms: How long the key was held down, in milliseconds.
            None if the release was not captured.
        flight_ms: Time gap since the previous keystroke, in milliseconds.
            None for the first event in a session.
    """

    timestamp: datetime
    key_label: str
    category: KeyCategory = KeyCategory.UNKNOWN
    window_title: str | None = None
    dwell_ms: float | None = None
    flight_ms: float | None = None

    def to_dict(self) -> dict[str, str | float | None]:
        """Serialize to a JSON-compatible dictionary."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "key": self.key_label,
            "category": self.category.name.lower(),
            "window": self.window_title or "unknown",
            "dwell_ms": self.dwell_ms,
            "flight_ms": self.flight_ms,
        }

    def to_log_line(self) -> str:
        """Format as a single log line for plaintext output."""
        ts = self.timestamp.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        window = f" [{self.window_title}]" if self.window_title else ""
        dwell = f" dwell={self.dwell_ms:.1f}ms" if self.dwell_ms is not None else ""
        flight = (
            f" flight={self.flight_ms:.1f}ms" if self.flight_ms is not None else ""
        )
        return f"[{ts}]{window} {self.key_label}{dwell}{flight}"


@dataclass
class SessionStats:
    """
    Aggregated typing metrics for a capture session.

    Populated by the biometrics analyzer from a stream of InputEvents.
    """

    duration_secs: float = 0.0
    total_keystrokes: int = 0
    words_per_minute: float = 0.0
    avg_dwell_ms: float = 0.0
    avg_flight_ms: float = 0.0
    top_keys: list[tuple[str, int]] = field(default_factory=list)
    category_distribution: dict[str, int] = field(default_factory=dict)
    rhythm_consistency: float = 0.0  # 0.0 = erratic, 1.0 = perfectly consistent

    def summary(self) -> str:
        """Human-readable analytics summary."""
        lines = [
            "",
            "═══════════════════════════════════════════",
            "         TYPING ANALYTICS REPORT           ",
            "═══════════════════════════════════════════",
            "",
            f"  Duration        : {self.duration_secs:.1f}s",
            f"  Total Keystrokes: {self.total_keystrokes}",
            f"  Typing Speed    : {self.words_per_minute:.1f} WPM",
            f"  Avg Dwell Time  : {self.avg_dwell_ms:.1f} ms",
            f"  Avg Flight Time : {self.avg_flight_ms:.1f} ms",
            f"  Rhythm Score    : {self.rhythm_consistency:.2f} / 1.00",
            "",
        ]

        if self.top_keys:
            lines.append("  Top Keys:")
            for key, count in self.top_keys[:10]:
                bar = "█" * min(count, 30)
                lines.append(f"    {key:>12s} : {count:4d}  {bar}")
            lines.append("")

        if self.category_distribution:
            lines.append("  Category Breakdown:")
            total = max(sum(self.category_distribution.values()), 1)
            for cat, count in sorted(
                self.category_distribution.items(), key=lambda x: -x[1]
            ):
                pct = count / total * 100
                lines.append(f"    {cat:>12s} : {pct:5.1f}%")
            lines.append("")

        lines.append("═══════════════════════════════════════════")
        return "\n".join(lines)
