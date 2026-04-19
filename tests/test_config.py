"""Tests for keystroke_analytics.config."""

import json
import tempfile
from pathlib import Path

from keystroke_analytics.config import (
    AppConfig,
    CaptureConfig,
    StorageConfig,
    AnalyticsConfig,
    WebhookConfig,
)


class TestDefaults:
    def test_capture_defaults(self):
        c = CaptureConfig()
        assert c.log_special_keys is True
        assert c.track_windows is True
        assert c.window_poll_interval == 0.5

    def test_storage_defaults(self):
        s = StorageConfig()
        assert s.max_file_size_mb == 5.0
        assert s.encrypt is False
        assert s.passphrase is None

    def test_analytics_defaults(self):
        a = AnalyticsConfig()
        assert a.enabled is True
        assert a.show_report_on_exit is True

    def test_webhook_defaults(self):
        w = WebhookConfig()
        assert w.url is None
        assert w.batch_size == 50

    def test_app_config_defaults(self):
        cfg = AppConfig()
        assert isinstance(cfg.capture, CaptureConfig)
        assert isinstance(cfg.storage, StorageConfig)
        assert isinstance(cfg.analytics, AnalyticsConfig)
        assert isinstance(cfg.webhook, WebhookConfig)


class TestFromFile:
    def test_load_json(self):
        data = {
            "capture": {"log_special_keys": False},
            "storage": {"max_file_size_mb": 10.0, "encrypt": True},
            "analytics": {"enabled": False},
            "webhook": {"url": "https://example.com", "batch_size": 25},
        }
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        ) as f:
            json.dump(data, f)
            f.flush()
            path = Path(f.name)

        cfg = AppConfig.from_file(path)
        path.unlink()

        assert cfg.capture.log_special_keys is False
        assert cfg.storage.max_file_size_mb == 10.0
        assert cfg.storage.encrypt is True
        assert cfg.analytics.enabled is False
        assert cfg.webhook.url == "https://example.com"
        assert cfg.webhook.batch_size == 25

    def test_partial_json_keeps_defaults(self):
        data = {"storage": {"encrypt": True}}
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        ) as f:
            json.dump(data, f)
            f.flush()
            path = Path(f.name)

        cfg = AppConfig.from_file(path)
        path.unlink()

        assert cfg.storage.encrypt is True
        # Other defaults preserved.
        assert cfg.capture.log_special_keys is True
        assert cfg.analytics.enabled is True

    def test_log_dir_as_string(self):
        data = {"storage": {"log_dir": "/tmp/test_logs"}}
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        ) as f:
            json.dump(data, f)
            f.flush()
            path = Path(f.name)

        cfg = AppConfig.from_file(path)
        path.unlink()

        assert cfg.storage.log_dir == Path("/tmp/test_logs")
