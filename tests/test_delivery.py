"""Tests for keystroke_analytics.delivery.webhook."""

from datetime import datetime
from unittest.mock import patch, MagicMock

from keystroke_analytics.models import InputEvent, KeyCategory
from keystroke_analytics.delivery.webhook import WebhookSender


def _event(key="a"):
    return InputEvent(
        timestamp=datetime(2026, 1, 1),
        key_label=key,
        category=KeyCategory.ALPHA,
    )


class TestWebhookSender:
    def test_disabled_without_url(self):
        ws = WebhookSender(url=None)
        assert not ws.enabled

    def test_enabled_with_url(self):
        ws = WebhookSender(url="https://example.com")
        assert ws.enabled

    def test_noop_when_disabled(self):
        ws = WebhookSender(url=None)
        ws.add_event(_event())
        assert ws.pending_count == 0

    def test_buffer_accumulates(self):
        ws = WebhookSender(url="https://example.com", batch_size=10)
        for _ in range(5):
            ws.add_event(_event())
        assert ws.pending_count == 5

    @patch("keystroke_analytics.delivery.webhook._requests")
    def test_batch_fires_at_threshold(self, mock_req):
        mock_req.post.return_value = MagicMock(ok=True)
        ws = WebhookSender(url="https://example.com", batch_size=3)
        for _ in range(3):
            ws.add_event(_event())
        mock_req.post.assert_called_once()
        assert ws.pending_count == 0

    @patch("keystroke_analytics.delivery.webhook._requests")
    def test_flush_sends_remaining(self, mock_req):
        mock_req.post.return_value = MagicMock(ok=True)
        ws = WebhookSender(url="https://example.com", batch_size=100)
        ws.add_event(_event())
        assert ws.pending_count == 1
        ws.flush()
        mock_req.post.assert_called_once()
        assert ws.pending_count == 0

    @patch("keystroke_analytics.delivery.webhook._requests")
    def test_payload_structure(self, mock_req):
        mock_req.post.return_value = MagicMock(ok=True)
        ws = WebhookSender(url="https://example.com", batch_size=1)
        ws.add_event(_event("z"))
        call_args = mock_req.post.call_args
        payload = call_args.kwargs["json"]
        assert "timestamp" in payload
        assert "host" in payload
        assert payload["event_count"] == 1
        assert payload["events"][0]["key"] == "z"
