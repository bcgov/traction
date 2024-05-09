from contextvars import ContextVar
import logging

from aries_cloudagent.config.injection_context import InjectionContext
from aries_cloudagent.core.event_bus import EventBus
from aries_cloudagent.core.plugin_registry import PluginRegistry
from aries_cloudagent.core.protocol_registry import ProtocolRegistry
from aries_cloudagent.config.logging import TimedRotatingFileMultiProcessHandler

from pythonjsonlogger import jsonlogger

from .holder_revocation_service import subscribe, HolderRevocationService

LOGGER = logging.getLogger(__name__)

LOG_FORMAT_PATTERN = (
    "%(asctime)s  TENANT: %(tenant_id)s %(levelname)s %(pathname)s:%(lineno)d %(message)s"
)


class ContextFilter(logging.Filter):
    """Custom logging filter to adapt logs with contextual tenant_id."""

    def __init__(self):
        """Initialize an instance of logging filter."""

        super(ContextFilter, self).__init__()

    def filter(self, record):
        """Filter log records and add tenant id to them."""

        if not hasattr(record, 'tenant_id') or not record.tenant_id:
            record.tenant_id = None
        return True


def setup_multitenant_logging():
    """Setup method for multitenant logging"""

    root_logger = logging.getLogger()
    for handler in root_logger.handlers:
        handler.setFormatter(
            logging.Formatter(LOG_FORMAT_PATTERN)
        )
        handler.addFilter(ContextFilter())


def log_records_inject(tenant_id: str):
    """Injects tenant_id into log records"""

    prev_log_record_factory = logging.getLogRecordFactory()
    def new_log_record_factory(*args, **kwargs):
        record = prev_log_record_factory(*args, **kwargs)
        record.tenant_id = tenant_id
        return record
    logging.setLogRecordFactory(new_log_record_factory)


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
