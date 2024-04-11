import logging

from aries_cloudagent.config.injection_context import InjectionContext
from aries_cloudagent.core.event_bus import EventBus
from aries_cloudagent.core.plugin_registry import PluginRegistry
from aries_cloudagent.core.protocol_registry import ProtocolRegistry
from aries_cloudagent.config.logging import TimedRotatingFileMultiProcessHandler

from pythonjsonlogger import jsonlogger

from .holder_revocation_service import subscribe, HolderRevocationService
from .routes import context_tenant_id

LOGGER = logging.getLogger(__name__)

LOG_FORMAT_FILE_ALIAS_PATTERN = (
    "%(asctime)s %(tenant_id)s %(levelname)s %(pathname)s:%(lineno)d %(message)s"
)


class ContextFilter(logging.Filter):
    """Custom logging filter to adapt logs with contextual tenant_id."""

    def __init__(self):
        """Initialize an instance of logging filter."""
        super(ContextFilter, self).__init__()

    def filter(self, record):
        """Filter log records and add tenant id to them."""
        try:
            tenant_id = context_tenant_id.get()
            record.tenant_id = tenant_id
        except LookupError:
            record.tenant_id = None

        return True


def setup_multitenant_logging():
    """Setup method for multitenant logging"""

    log_filter = ContextFilter()
    for handler in logging.root.handlers:
        if isinstance(handler, TimedRotatingFileMultiProcessHandler):
            # Set log formatter to inject tenant id
            handler.setFormatter(
                jsonlogger.JsonFormatter(LOG_FORMAT_FILE_ALIAS_PATTERN)
            )
        handler.addFilter(log_filter)


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
