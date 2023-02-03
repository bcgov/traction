import logging
import re

from aries_cloudagent.config.injection_context import InjectionContext
from aries_cloudagent.connections.models.conn_record import ConnRecord

from aries_cloudagent.core.event_bus import EventBus, Event
from aries_cloudagent.core.plugin_registry import PluginRegistry
from aries_cloudagent.core.profile import Profile
from aries_cloudagent.core.protocol_registry import ProtocolRegistry
from aries_cloudagent.core.util import STARTUP_EVENT_PATTERN

from . import schema_storage, creddef_storage, endorser, connections, tenant
from .config import get_config
from .tenant_manager import TenantManager

MODULES = [
    connections,
    endorser,
    creddef_storage,
    schema_storage,
    tenant,
]

LOGGER = logging.getLogger(__name__)

CONNECTIONS_EVENT_PATTERN = re.compile(f"acapy::record::{ConnRecord.RECORD_TOPIC}::.*")


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

    bus.subscribe(STARTUP_EVENT_PATTERN, on_startup)

    # load all other sub modules/plugins...
    if context.settings.get("multitenant.enabled"):
        LOGGER.info("> > setup plugins...")
        for mod in MODULES:
            # call the setup explicitly...
            await mod.setup(context)
            # do this to load routes...
            plugin_registry.register_plugin(mod.__name__)
        LOGGER.info("< < setup plugins.")

    LOGGER.info("< plugin setup.")


async def on_startup(profile: Profile, event: Event):
    LOGGER.info("> on_startup")
    if profile.context.settings.get("multitenant.enabled"):
        # create a tenant manager, this will use the root profile for its sessions
        # this will create reservations and tenants under the same profile (base/root) as wallets
        _config = get_config(profile.settings)
        mgr = TenantManager(profile, _config)
        profile.context.injector.bind_instance(TenantManager, mgr)
        await mgr.create_innkeeper()
    else:
        # what type of error should this throw?
        raise ValueError(
            "'multitenant' is not enabled, cannot load 'traction_innkeeper' plugin"
        )

    LOGGER.info("< on_startup")
