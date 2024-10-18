import logging

from acapy_agent.config.injection_context import InjectionContext
from acapy_agent.core.event_bus import EventBus
from acapy_agent.core.plugin_registry import PluginRegistry
from acapy_agent.core.protocol_registry import ProtocolRegistry

from .schema_storage_service import SchemaStorageService, subscribe

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

    srv = SchemaStorageService()
    context.injector.bind_instance(SchemaStorageService, srv)

    subscribe(bus)

    LOGGER.info("< plugin setup.")
