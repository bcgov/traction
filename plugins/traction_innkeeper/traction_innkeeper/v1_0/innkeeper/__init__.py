import logging
import re

from acapy_agent.config.injection_context import InjectionContext
from acapy_agent.connections.models.conn_record import ConnRecord

from acapy_agent.core.event_bus import EventBus, Event
from acapy_agent.core.plugin_registry import PluginRegistry
from acapy_agent.core.profile import Profile
from acapy_agent.core.protocol_registry import ProtocolRegistry
from acapy_agent.core.util import STARTUP_EVENT_PATTERN

from .config import get_config
from .tenant_manager import TenantManager

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
