import logging

from aries_cloudagent.config.injection_context import InjectionContext
from aries_cloudagent.core.event_bus import EventBus, Event
from aries_cloudagent.core.profile import Profile
from aries_cloudagent.core.protocol_registry import ProtocolRegistry
from aries_cloudagent.core.util import STARTUP_EVENT_PATTERN

from .tenant_manager import TenantManager

LOGGER = logging.getLogger(__name__)


async def setup(context: InjectionContext):
    LOGGER.info("> plugin setup...")

    protocol_registry = context.inject(ProtocolRegistry)
    if not protocol_registry:
        raise ValueError("ProtocolRegistry missing in context")

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
        mgr = TenantManager(profile)
        profile.context.injector.bind_instance(TenantManager, mgr)
        await mgr.create_innkeeper()
    else:
        # what type of error should this throw?
        raise ValueError(
            "'multitenant' is not enabled, cannot load 'traction_innkeeper' plugin"
        )

    LOGGER.info("< on_startup")
