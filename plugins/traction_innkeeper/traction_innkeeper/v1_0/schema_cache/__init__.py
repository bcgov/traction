import logging

from aries_cloudagent.config.injection_context import InjectionContext
from aries_cloudagent.core.event_bus import EventBus, Event
from aries_cloudagent.core.plugin_registry import PluginRegistry
from aries_cloudagent.core.profile import Profile
from aries_cloudagent.core.protocol_registry import ProtocolRegistry

from aries_cloudagent.messaging.schemas.util import (
    EVENT_LISTENER_PATTERN as SCHEMAS_EVENT_LISTENER_PATTERN,
)

from .models import SchemaCacheRecord
from .schema_cache_service import add_schema_to_cache

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

    bus.subscribe(SCHEMAS_EVENT_LISTENER_PATTERN, schemas_event_handler)

    LOGGER.info("< plugin setup.")


async def schemas_event_handler(profile: Profile, event: Event):
    LOGGER.info("> schemas_event_handler")
    LOGGER.debug(f"profile = {profile}")
    LOGGER.debug(f"event = {event}")

    schema_id = event.payload["context"]["schema_id"]
    schema_cache_record = await add_schema_to_cache(profile, schema_id)
    LOGGER.debug(f"schema_cache_record = {schema_cache_record}")
    await add_schema_to_cache(profile, schema_id)

    LOGGER.info("< schemas_event_handler")
