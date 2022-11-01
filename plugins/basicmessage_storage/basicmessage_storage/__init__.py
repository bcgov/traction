import logging
import re

from aries_cloudagent.config.injection_context import InjectionContext
from aries_cloudagent.core.event_bus import EventBus, Event
from aries_cloudagent.core.profile import Profile
from aries_cloudagent.core.protocol_registry import ProtocolRegistry
from aries_cloudagent.core.plugin_registry import PluginRegistry
from aries_cloudagent.protocols.basicmessage.definition import versions
from aries_cloudagent.protocols.basicmessage.v1_0.message_types import MESSAGE_TYPES

from .models import BasicMessageRecord

LOGGER = logging.getLogger(__name__)

BASIC_MESSAGE_EVENT_PATTERN = re.compile("^acapy::basicmessage::received$")


async def setup(context: InjectionContext):
    LOGGER.info("> plugin setup...")
    protocol_registry = context.inject(ProtocolRegistry)
    assert protocol_registry

    # unregister basicmessage, manually register message types not the routes
    plugin_registry = context.inject(PluginRegistry)
    assert plugin_registry
    plugin_registry._plugins.pop("aries_cloudagent.protocols.basicmessage")

    # register basicmessage message types...
    protocol_registry.register_message_types(
        MESSAGE_TYPES, version_definition=versions[0]
    )

    event_bus = context.inject(EventBus)
    if not event_bus:
        raise ValueError("EventBus missing in context")

    event_bus.subscribe(BASIC_MESSAGE_EVENT_PATTERN, basic_message_event_handler)
    LOGGER.info("< plugin setup.")


async def basic_message_event_handler(profile: Profile, event: Event):
    #LOGGER.info(event.payload)
    # grab the received event and persist it.
    msg: BasicMessageRecord = BasicMessageRecord.deserialize(event.payload)
    msg.state = BasicMessageRecord.STATE_RECV
    async with profile.session() as session:
        await msg.save(session, reason="New received message")

