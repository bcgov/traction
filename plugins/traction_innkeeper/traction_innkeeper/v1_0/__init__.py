import logging


from acapy_agent.config.injection_context import InjectionContext


from acapy_agent.core.event_bus import EventBus
from acapy_agent.core.plugin_registry import PluginRegistry
from acapy_agent.core.protocol_registry import ProtocolRegistry

from . import (
    schema_storage,
    creddef_storage,
    endorser,
    connections,
    tenant,
    innkeeper,
    oca,
)

MODULES = [
    oca,
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
