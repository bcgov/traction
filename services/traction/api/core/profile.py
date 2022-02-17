"""Classes for managing profile information within a request context."""

import logging

from abc import ABC
from typing import Any

from api.core.config import settings
from api.core.event_bus import Event


LOGGER = logging.getLogger(__name__)


class Profile(ABC):
    """Base abstraction for handling identity-related state."""

    def __init__(
        self,
        wallet_id: str,
    ):
        """Initialize a base profile."""
        self._wallet_id = wallet_id

    @property
    def wallet_id(self):
        """Return this event's wallet_id."""
        return self._wallet_id

    async def notify(self, topic: str, payload: Any):
        """Signal an event."""
        await settings.EVENT_BUS.notify(self, Event(topic, payload))
