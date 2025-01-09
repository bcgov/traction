import logging
import re

from acapy_agent.config.injector import Injector
from acapy_agent.connections.models.conn_record import ConnRecord
from acapy_agent.core.event_bus import Event, EventBus
from acapy_agent.core.profile import Profile
from acapy_agent.protocols.didexchange.v1_0.manager import DIDXManager
from acapy_agent.protocols.endorse_transaction.v1_0.manager import (
    TransactionManager,
)


from ..innkeeper.tenant_manager import TenantManager


CONNECTIONS_EVENT_PATTERN = re.compile(f"acapy::record::{ConnRecord.RECORD_TOPIC}::.*")

LOGGER = logging.getLogger(__name__)


class EndorserConnectionService:
    def __init__(self):
        """
        Initialize a EndorserConnectionService.

        Args:
            context: The context for this credential
        """
        self._logger = logging.getLogger(__name__)

    @property
    def logger(self) -> logging.Logger:
        return self._logger

    def endorser_alias(self, profile: Profile):
        value = profile.settings.get("endorser.endorser_alias")
        return value

    def endorser_public_did(self, profile: Profile):
        value = profile.settings.get("endorser.endorser_public_did")
        return value

    def endorser_info(self, profile: Profile):
        self.logger.info("> endorser_info()")
        alias = self.endorser_alias(profile)
        did = self.endorser_public_did(profile)
        result = None
        if alias and did:
            # return connection endorser_info struct
            result = {
                "endorser_did": did,
                "endorser_name": alias,
            }

        self.logger.info(f"< endorser_info(): {result}")
        return result

    async def endorser_connection(self, profile: Profile):
        self.logger.info("> endorser_connection()")
        info = self.endorser_info(profile)
        result = None
        if info:
            async with profile.session() as session:
                conn_recs = await ConnRecord.retrieve_by_alias(
                    session, alias=info["endorser_name"]
                )
                if len(conn_recs):
                    result = conn_recs[0]

        self.logger.info(f"< endorser_connection(): {result}")
        return result

    async def connect_with_endorser(self, profile: Profile, context: Injector):
        self.logger.info("> connect_with_endorser()")
        info = self.endorser_info(profile)
        result = None
        if info:
            result = await self.endorser_connection(profile)
            if not result:
                self.logger.info("no connection to endorser, initiate one...")
                wallet_id = profile.settings.get("wallet.id")
                tenant_mgr = context.inject(TenantManager)
                wallet_rec, tenant_rec = await tenant_mgr.get_wallet_and_tenant(
                    wallet_id
                )
                self.logger.info(f"wallet id = {wallet_id}")
                self.logger.info(f"wallet_rec = {wallet_rec}")
                self.logger.info(f"tenant_rec = {tenant_rec}")
                my_label = (
                    tenant_rec.tenant_name if tenant_rec else wallet_rec.wallet_name
                )
                self.logger.info(f"my_label = {my_label}")

                # this call is lifted from:
                # didexchange / v1_0 / routes.py -> didx_create_request_implicit
                didx_mgr = DIDXManager(profile)
                result = await didx_mgr.create_request_implicit(
                    their_public_did=info["endorser_did"],
                    alias=info["endorser_name"],
                    my_label=my_label,
                )

        self.logger.info(f"< connect_with_endorser(): {result}")
        return result


def subscribe(bus: EventBus):
    bus.subscribe(CONNECTIONS_EVENT_PATTERN, connections_event_handler)


async def connections_event_handler(profile: Profile, event: Event):
    LOGGER.info("> connections_event_handler")
    LOGGER.debug(f"profile = {profile}")
    LOGGER.debug(f"event = {event}")
    record: ConnRecord = ConnRecord.deserialize(event.payload)
    LOGGER.debug(f"record = {record}")

    endorser_alias = profile.settings.get("endorser.endorser_alias")
    connection_id = record.connection_id
    if record.alias == endorser_alias:
        LOGGER.info("connection is with endorser...")
        # when record is first set to complete/active, we need to add metadata.
        if record.state == ConnRecord.State.COMPLETED:
            async with profile.session() as session:
                conn_metadata = await record.metadata_get_all(session)
                LOGGER.debug(f"conn_metadata = {conn_metadata}")
            has_endorser_metadata = False
            if "transaction-jobs" in conn_metadata:
                if "transaction_my_job" in conn_metadata["transaction-jobs"]:
                    has_endorser_metadata = True
            LOGGER.info(f"has endorser metadata? {has_endorser_metadata}")

            if not has_endorser_metadata:
                # set connection id endorser role
                transaction_mgr = TransactionManager(profile)
                tx_job_to_send = await transaction_mgr.set_transaction_my_job(
                    record=record, transaction_my_job="TRANSACTION_AUTHOR"
                )
                LOGGER.debug(f"tx_job_to_send = {tx_job_to_send}")

                async with profile.session() as session:
                    conn_rec = await ConnRecord.retrieve_by_id(session, connection_id)
                    jobs = await conn_rec.metadata_get(session, "transaction_jobs")
                    LOGGER.debug(f"jobs = {jobs}")

                    # set endorser metadata on connection...
                    endorser_public_did = profile.settings.get(
                        "endorser.endorser_public_did"
                    )
                    value = {
                        "endorser_did": endorser_public_did,
                        "endorser_name": endorser_alias,
                    }
                    await conn_rec.metadata_set(
                        session, key="endorser_info", value=value
                    )
                    endorser_info = await conn_rec.metadata_get(
                        session, "endorser_info"
                    )
                    LOGGER.info(f"added endorser metadata = {endorser_info}")

    LOGGER.info("< connections_event_handler")
