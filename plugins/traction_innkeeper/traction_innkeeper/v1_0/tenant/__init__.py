import logging
from contextvars import ContextVar
from typing import Optional

from acapy_agent.config.injection_context import InjectionContext
from acapy_agent.core.event_bus import EventBus
from acapy_agent.core.plugin_registry import PluginRegistry
from acapy_agent.core.protocol_registry import ProtocolRegistry

from .holder_revocation_service import subscribe, HolderRevocationService

LOGGER = logging.getLogger(__name__)

context_tenant_id: ContextVar[Optional[str]] = ContextVar("context_tenant_id", default=None)


class ContextFilter(logging.Filter):
    """Custom logging filter to adapt logs with contextual tenant_id."""

    def __init__(self):
        """Initialize an instance of logging filter."""

        super(ContextFilter, self).__init__()

    def filter(self, record):
        """Filter log records and add tenant id to them."""

        record.tenant_id = context_tenant_id.get()
        return True


def setup_multitenant_logging():
    """Attach the tenant_id filter to the root handlers.

    Formatters are left untouched so the configured log format (e.g. JSON) is kept.
    """

    root_logger = logging.getLogger()
    for handler in root_logger.handlers:
        handler.addFilter(ContextFilter())


def log_records_inject(tenant_id: Optional[str]):
    """Sets the tenant_id for log records emitted in the current request context"""

    context_tenant_id.set(tenant_id)


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

    srv = HolderRevocationService()
    context.injector.bind_instance(HolderRevocationService, srv)

    subscribe(bus)

    setup_multitenant_logging()

    LOGGER.info("< plugin setup.")
