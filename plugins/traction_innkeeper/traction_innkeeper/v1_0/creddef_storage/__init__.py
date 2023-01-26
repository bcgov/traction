import logging

from aries_cloudagent.config.injection_context import InjectionContext
from aries_cloudagent.core.event_bus import EventBus
from aries_cloudagent.core.plugin_registry import PluginRegistry

from aries_cloudagent.core.protocol_registry import ProtocolRegistry

from .creddef_storage_service import CredDefStorageService, subscribe

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

    srv = CredDefStorageService()
    context.injector.bind_instance(CredDefStorageService, srv)

    subscribe(bus)

    LOGGER.info("< plugin setup.")
