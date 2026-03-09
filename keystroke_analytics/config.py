"""
Configuration management for keystroke analytics.

Supports loading from YAML or JSON files, with sensible defaults.
All paths are resolved at load time so the rest of the application
can use them without worrying about relative vs absolute.
"""

import json
import logging
from pathlib import Path
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class CaptureConfig:
    """Settings for the keystroke capture subsystem."""

    log_special_keys: bool = True
    track_windows: bool = True
    window_poll_interval: float = 0.5


@dataclass
class StorageConfig:
    """Settings for log file output and rotation."""

    log_dir: Path = field(default_factory=lambda: Path.home() / ".keystroke_analytics")
    file_prefix: str = "session"
    max_file_size_mb: float = 5.0
    encrypt: bool = False
    passphrase: str | None = None


@dataclass
class AnalyticsConfig:
    """Settings for the biometrics analyzer."""

    enabled: bool = True
    show_report_on_exit: bool = True


@dataclass
class WebhookConfig:
    """Settings for remote event delivery."""

    url: str | None = None
    batch_size: int = 50
    timeout_secs: float = 5.0


@dataclass
class AppConfig:
    """
    Top-level application configuration.

    Can be constructed from defaults, or loaded from a YAML/JSON file
    via ``AppConfig.from_file(path)``.
    """

    capture: CaptureConfig = field(default_factory=CaptureConfig)
    storage: StorageConfig = field(default_factory=StorageConfig)
    analytics: AnalyticsConfig = field(default_factory=AnalyticsConfig)
    webhook: WebhookConfig = field(default_factory=WebhookConfig)

    @classmethod
    def from_file(cls, path: Path) -> "AppConfig":
        """Load configuration from a YAML or JSON file.

        Keys in the file map to the nested dataclass fields.  Missing
        keys keep their default values.

        Example YAML::

            capture:
              log_special_keys: true
            storage:
              encrypt: true
              passphrase: "my-secret"
            analytics:
              enabled: true
        """
        text = path.read_text(encoding="utf-8")

        if path.suffix in (".yaml", ".yml"):
            try:
                import yaml  # type: ignore[import-untyped]

                raw = yaml.safe_load(text) or {}
            except ImportError:
                logger.warning("PyYAML not installed; falling back to JSON parser")
                raw = json.loads(text)
        else:
            raw = json.loads(text)

        return cls._from_dict(raw)

    @classmethod
    def _from_dict(cls, data: dict) -> "AppConfig":
        """Build an AppConfig from a plain dictionary."""
        capture = CaptureConfig(**data.get("capture", {}))

        storage_raw = data.get("storage", {})
        if "log_dir" in storage_raw:
            storage_raw["log_dir"] = Path(storage_raw["log_dir"])
        storage = StorageConfig(**storage_raw)

        analytics = AnalyticsConfig(**data.get("analytics", {}))
        webhook = WebhookConfig(**data.get("webhook", {}))

        return cls(
            capture=capture,
            storage=storage,
            analytics=analytics,
            webhook=webhook,
        )
