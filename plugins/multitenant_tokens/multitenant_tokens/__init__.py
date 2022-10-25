import os
import logging

from aries_cloudagent.config.injection_context import InjectionContext
from aries_cloudagent.core.protocol_registry import ProtocolRegistry
from aries_cloudagent.admin.base_server import BaseAdminServer

from aries_cloudagent.core.util import SHUTDOWN_EVENT_PATTERN, STARTUP_EVENT_PATTERN
from aries_cloudagent.core.event_bus import Event, EventBus, EventWithMetadata
from aries_cloudagent.core.profile import Profile
from aries_cloudagent.multitenant.base import BaseMultitenantManager

from .provider import TractionMultitenantManagerProvider

LOGGER = logging.getLogger(__name__)

async def setup(context: InjectionContext):
    LOGGER.info("> plugin setup...")
    protocol_registry = context.inject(ProtocolRegistry)
    assert protocol_registry
    LOGGER.info("< plugin setup.")

    bus = context.inject(EventBus)
    if not bus:
        raise ValueError("EventBus missing in context")

    bus.subscribe(STARTUP_EVENT_PATTERN, on_startup)



async def on_startup(profile: Profile, event: Event):
    LOGGER.info("> on_startup")
    if profile.context.settings.get("multitenant.enabled"):
        # need to replace some multi tenant managers... anything that was created during start up
        # override the default factory...
        profile.context.injector.bind_provider(BaseMultitenantManager, TractionMultitenantManagerProvider(profile))

        # the AdminServer was created with the old one injected
        # replace it...
        srv = profile.context.inject(BaseAdminServer)
        srv.multitenant_manager = profile.context.inject(BaseMultitenantManager)
    else:
        # what type of error should this throw?
        raise ValueError("'multitenant' is not enabled, cannot load 'multitenant_tokens' plugin")  
         
    LOGGER.info("< on_startup")
