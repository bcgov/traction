import logging

from aries_cloudagent.config.injection_context import InjectionContext
from aries_cloudagent.core.event_bus import EventBus, Event
from aries_cloudagent.core.plugin_registry import PluginRegistry
from aries_cloudagent.core.profile import Profile
from aries_cloudagent.core.protocol_registry import ProtocolRegistry

from aries_cloudagent.messaging.credential_definitions.util import (
    EVENT_LISTENER_PATTERN as CREDDEF_EVENT_LISTENER_PATTERN,
)

from .creddef_storage_service import add_item

LOGGER = logging.getLogger(__name__)


async def setup(context: InjectionContext):
    LOGGER.info("> plugin setup...")

    protocol_registry = context.inject(ProtocolRegistry)
    if not protocol_registry:
        raise ValueError("ProtocolRegistry missing in context")

    plugin_registry = context.inject(PluginRegistry)
    if not plugin_registry:
        raise ValueError("PluginRegistry missing in context")

    bus = context.inject(EventBus)
    if not bus:
        raise ValueError("EventBus missing in context")

    bus.subscribe(CREDDEF_EVENT_LISTENER_PATTERN, creddef_event_handler)

    LOGGER.info("< plugin setup.")


async def creddef_event_handler(profile: Profile, event: Event):
    LOGGER.info("> creddef_event_handler")
    LOGGER.debug(f"profile = {profile}")
    LOGGER.debug(f"event = {event}")
    storage_record = await add_item(profile, event.payload["context"])
    LOGGER.debug(f"creddef_storage_record = {storage_record}")

    LOGGER.info("< creddef_event_handler")
