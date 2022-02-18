"""Classes for managing profile information within a request context."""

import logging

from abc import ABC
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from api.core.config import settings
from api.core.event_bus import Event


LOGGER = logging.getLogger(__name__)


class Profile(ABC):
    """Base abstraction for handling identity-related state."""

    def __init__(
        self,
        wallet_id: str,
        db: AsyncSession,
    ):
        """Initialize a base profile."""
        self._wallet_id = wallet_id
        self._db = db

    @property
    def wallet_id(self):
        """Return this event's wallet_id."""
        return self._wallet_id

    @property
    def db(self):
        """Return this event's db session."""
        return self._db

    async def notify(self, topic: str, payload: Any):
        """Signal an event."""
        await settings.EVENT_BUS.notify(self, Event(topic, payload))
