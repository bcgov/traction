import logging
import re

from acapy_agent.config.injection_context import InjectionContext
from acapy_agent.core.event_bus import EventBus, Event
from acapy_agent.core.profile import Profile
from acapy_agent.core.plugin_registry import PluginRegistry
from acapy_agent.core.protocol_registry import ProtocolRegistry

from .holder_revocation_service import subscribe, HolderRevocationService

LOGGER = logging.getLogger(__name__)

LOG_FORMAT_PATTERN = "%(asctime)s  TENANT: %(tenant_id)s %(levelname)s %(pathname)s:%(lineno)d %(message)s"

base_log_record_factory = logging.getLogRecordFactory()


class ContextFilter(logging.Filter):
    """Custom logging filter to adapt logs with contextual tenant_id."""

    def __init__(self):
        """Initialize an instance of logging filter."""

        super(ContextFilter, self).__init__()

    def filter(self, record):
        """Filter log records and add tenant id to them."""

        if not hasattr(record, "tenant_id") or not record.tenant_id:
            record.tenant_id = None
        return True


def setup_multitenant_logging():
    """Setup method for multitenant logging"""

    root_logger = logging.getLogger()
    for handler in root_logger.handlers:
        handler.setFormatter(logging.Formatter(LOG_FORMAT_PATTERN))
        handler.addFilter(ContextFilter())


def log_records_inject(tenant_id: str):
    """Injects tenant_id into log records"""

    try:

        def modded_log_record_factory(*args, **kwargs):
            record = base_log_record_factory(*args, **kwargs)
            record.tenant_id = tenant_id
            return record

        logging.setLogRecordFactory(modded_log_record_factory)
    except Exception as e:  # pylint: disable=broad-except
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

    # Subscribe to issuer credential revocation record events
    # This event is emitted when an IssuerCredRevRecord state changes to 'revoked'
    # The event name is: acapy::record::issuer_cred_rev::revoked
    # (Note: The old event name acapy::cred-revoked may no longer be emitted)
    ISSUER_CRED_REV_REVOKED_EVENT_PATTERN = re.compile(
        r"^acapy::record::issuer_cred_rev::revoked$"
    )
    bus.subscribe(
        ISSUER_CRED_REV_REVOKED_EVENT_PATTERN, issuer_cred_rev_revoked_handler
    )

    setup_multitenant_logging()

    LOGGER.info("< plugin setup.")


async def issuer_cred_rev_revoked_handler(profile: Profile, event: Event):
    """Handle issuer credential revocation record revoked event.
    
    This event is emitted when an IssuerCredRevRecord state changes to 'revoked'.
    The event payload is the IssuerCredRevRecord.
    
    Note: ACA-Py subscribes to 'acapy::cred-revoked' but the actual event emitted
    is 'acapy::record::issuer_cred_rev::revoked', so we need to handle it here to
    update the credential exchange state.
    """
    LOGGER.info("> issuer_cred_rev_revoked_handler")
    from acapy_agent.protocols.issue_credential.v2_0.models.cred_ex_record import (
        V20CredExRecord,
    )
    from acapy_agent.revocation.models.issuer_cred_rev_record import (
        IssuerCredRevRecord,
    )
    from acapy_agent.storage.error import StorageNotFoundError
    
    # The event payload is the IssuerCredRevRecord
    rev_rec = event.payload
    if not isinstance(rev_rec, IssuerCredRevRecord):
        LOGGER.warning("Event payload is not an IssuerCredRevRecord")
        return
    
    if rev_rec.cred_ex_id is None:
        LOGGER.debug("IssuerCredRevRecord has no cred_ex_id, skipping")
        return
    
    if (
        rev_rec.cred_ex_version
        and rev_rec.cred_ex_version != IssuerCredRevRecord.VERSION_2
    ):
        LOGGER.debug(
            "IssuerCredRevRecord version is %s, not VERSION_2, skipping",
            rev_rec.cred_ex_version
        )
        return
    
    # Update the credential exchange record state
    async with profile.transaction() as txn:
        try:
            cred_ex_record = await V20CredExRecord.retrieve_by_id(
                txn, rev_rec.cred_ex_id, for_update=True
            )
            cred_ex_record.state = V20CredExRecord.STATE_CREDENTIAL_REVOKED
            await cred_ex_record.save(txn, reason="revoke credential")
            await txn.commit()
            LOGGER.info(
                "Updated credential exchange %s state to credential-revoked",
                rev_rec.cred_ex_id
            )
        except StorageNotFoundError:
            LOGGER.warning(
                "Credential exchange record %s not found",
                rev_rec.cred_ex_id
            )
    
    LOGGER.info("< issuer_cred_rev_revoked_handler")
