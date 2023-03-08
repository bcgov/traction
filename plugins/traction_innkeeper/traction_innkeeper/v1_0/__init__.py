import logging


from aries_cloudagent.config.injection_context import InjectionContext


from aries_cloudagent.core.event_bus import EventBus, Event
from aries_cloudagent.core.plugin_registry import PluginRegistry
from aries_cloudagent.core.profile import Profile
from aries_cloudagent.core.protocol_registry import ProtocolRegistry
from aries_cloudagent.admin.server import EVENT_PATTERN_RECORD

from . import schema_storage, creddef_storage, endorser, connections, tenant, innkeeper

MODULES = [
    innkeeper,
    tenant,
    connections,
    endorser,
    creddef_storage,
    schema_storage,
]

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
    # probably only want this for debugging...
    bus.subscribe(EVENT_PATTERN_RECORD, on_event)

    # perform a pseudo load of the other "plugins"
    #
    # Load the modules "manually"...
    # do not register the modules as plugins in the plugin registry - causes race conditions and lock issues.
    #
    # if these modules are separated into real plugins, we will remove them from
    # the MODULES list and load like all other plugins.
    #
    # Note that we will also load the routes "manually" not through the plugin registry
    if context.settings.get("multitenant.enabled"):
        LOGGER.info("> > setup plugins...")
        for mod in MODULES:
            # call the setup explicitly...
            await mod.setup(context)
        LOGGER.info("< < setup plugins.")

    LOGGER.info("< plugin setup.")


async def on_event(profile: Profile, event: Event):
    LOGGER.info("> on_event")
    LOGGER.info(f"profile = {profile}")
    LOGGER.info(f"event = {event}")
    LOGGER.info("< on_event")
