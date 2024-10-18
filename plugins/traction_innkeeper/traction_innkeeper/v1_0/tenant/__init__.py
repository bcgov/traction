from contextvars import ContextVar
import logging

from acapy_agent.config.injection_context import InjectionContext
from acapy_agent.core.event_bus import EventBus
from acapy_agent.core.plugin_registry import PluginRegistry
from acapy_agent.core.protocol_registry import ProtocolRegistry
from acapy_agent.config.logging import TimedRotatingFileMultiProcessHandler

from pythonjsonlogger import jsonlogger

from .holder_revocation_service import subscribe, HolderRevocationService

LOGGER = logging.getLogger(__name__)

LOG_FORMAT_PATTERN = (
    "%(asctime)s  TENANT: %(tenant_id)s %(levelname)s %(pathname)s:%(lineno)d %(message)s"
)

base_log_record_factory = logging.getLogRecordFactory()

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

    try:
        def modded_log_record_factory(*args, **kwargs):
            record = base_log_record_factory(*args, **kwargs)
            record.tenant_id = tenant_id
            return record

        logging.setLogRecordFactory(modded_log_record_factory)
    except Exception as e: # pylint: disable=broad-except
        LOGGER.error("There was a problem injecting tenant_id into the logs: %s", e)

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
