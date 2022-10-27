import os
import logging

from aries_cloudagent.config.injection_context import InjectionContext
from aries_cloudagent.core.protocol_registry import ProtocolRegistry

LOGGER = logging.getLogger(__name__)

async def setup(context: InjectionContext):
    LOGGER.info("> plugin setup...")
    protocol_registry = context.inject(ProtocolRegistry)
    assert protocol_registry
    LOGGER.info("< plugin setup.")
