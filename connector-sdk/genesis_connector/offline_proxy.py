"""
Local offline proxy buffer for the GenesisConnector SDK.

When the network connection is lost, submitted actions are buffered here
instead of being dropped.  On reconnect, the caller drains the buffer
and re-submits the accumulated actions in chronological order.

Usage::

    proxy = OfflineProxy(max_size=50)

    # While disconnected:
    proxy.buffer_action(action_intent)

    # After reconnect:
    for action in proxy.drain():
        await connector.submit_action(action)
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class BufferedAction:
    """An action intent that was buffered while offline."""

    action: dict[str, Any]
    buffered_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class OfflineProxy:
    """
    In-memory ring-buffer for action intents submitted during a disconnect.

    Parameters
    ----------
    max_size:
        Maximum number of actions to retain.  When the buffer is full the
        **oldest** entry is silently evicted (deque maxlen semantics).
    """

    def __init__(self, max_size: int = 50) -> None:
        if max_size < 1:
            raise ValueError("max_size must be ≥ 1")
        self._queue: deque[BufferedAction] = deque(maxlen=max_size)
        self.max_size = max_size

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def buffer_action(self, action: dict[str, Any]) -> None:
        """Add *action* to the buffer.

        If the buffer is already full, the oldest entry is dropped
        automatically (ring-buffer semantics).
        """
        self._queue.append(BufferedAction(action=action))

    def drain(self) -> list[dict[str, Any]]:
        """Return all buffered actions in chronological order and clear the buffer.

        Returns
        -------
        list[dict]
            Actions in the order they were buffered (oldest first).
        """
        items = [entry.action for entry in self._queue]
        self._queue.clear()
        return items

    def peek(self) -> list[BufferedAction]:
        """Return buffered entries without consuming them."""
        return list(self._queue)

    def clear(self) -> None:
        """Discard all buffered actions without returning them."""
        self._queue.clear()

    # ------------------------------------------------------------------
    # Convenience helpers
    # ------------------------------------------------------------------

    def __len__(self) -> int:
        return len(self._queue)

    @property
    def is_empty(self) -> bool:
        """True when there are no buffered actions."""
        return len(self._queue) == 0

    @property
    def is_full(self) -> bool:
        """True when the buffer has reached its maximum capacity."""
        return len(self._queue) == self.max_size

    def __repr__(self) -> str:
        return f"OfflineProxy(size={len(self)}/{self.max_size})"
