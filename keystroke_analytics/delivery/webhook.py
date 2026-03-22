"""
Batched webhook delivery.

Buffers ``InputEvent`` objects and sends them in batches to a remote
HTTPS endpoint.  The buffer lock is released before the HTTP POST so
that capture is never blocked by network latency.
"""

import platform
import logging
from datetime import datetime
from threading import Lock

from keystroke_analytics.models import InputEvent

logger = logging.getLogger(__name__)

try:
    import requests as _requests
except ImportError:
    _requests = None  # type: ignore[assignment]


class WebhookSender:
    """
    Buffers events and POSTs them in batches to a webhook URL.

    Parameters:
        url: The HTTPS endpoint to deliver events to.
        batch_size: Number of events to buffer before sending.
        timeout_secs: HTTP request timeout.
    """

    def __init__(
        self,
        url: str | None = None,
        batch_size: int = 50,
        timeout_secs: float = 5.0,
    ) -> None:
        self._url = url
        self._batch_size = batch_size
        self._timeout = timeout_secs
        self._buffer: list[InputEvent] = []
        self._lock = Lock()
        self.enabled = bool(url and _requests)

    def add_event(self, event: InputEvent) -> None:
        """Buffer an event; send a batch when the threshold is reached."""
        if not self.enabled:
            return

        batch: list[InputEvent] | None = None
        with self._lock:
            self._buffer.append(event)
            if len(self._buffer) >= self._batch_size:
                batch = self._buffer
                self._buffer = []

        if batch:
            self._send(batch)

    def flush(self) -> None:
        """Force-send any remaining buffered events."""
        batch: list[InputEvent] | None = None
        with self._lock:
            if self._buffer:
                batch = self._buffer
                self._buffer = []

        if batch:
            self._send(batch)

    @property
    def pending_count(self) -> int:
        """Number of events currently buffered."""
        with self._lock:
            return len(self._buffer)

    # ------------------------------------------------------------------

    def _send(self, events: list[InputEvent]) -> None:
        if not self._url or _requests is None:
            return

        payload = {
            "timestamp": datetime.now().isoformat(),
            "host": platform.node(),
            "event_count": len(events),
            "events": [e.to_dict() for e in events],
        }

        try:
            resp = _requests.post(self._url, json=payload, timeout=self._timeout)
            if not resp.ok:
                logger.warning("Webhook HTTP %s", resp.status_code)
        except Exception:
            logger.error("Webhook delivery failed", exc_info=True)
