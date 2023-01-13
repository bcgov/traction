import logging

from aries_cloudagent.connections.models.conn_record import ConnRecord
from aries_cloudagent.core.event_bus import Event
from aries_cloudagent.core.profile import Profile
from aries_cloudagent.protocols.endorse_transaction.v1_0.manager import (
    TransactionManager,
)

LOGGER = logging.getLogger(__name__)


async def endorser_connections_event_handler(profile: Profile, event: Event):
    LOGGER.info("> endorser_connections_event_handler")
    LOGGER.debug(f"profile = {profile}")
    LOGGER.debug(f"event = {event}")
    record: ConnRecord = ConnRecord.deserialize(event.payload)
    LOGGER.debug(f"record = {record}")

    endorser_alias = profile.settings.get("endorser.endorser_alias")
    connection_id = record.connection_id
    if record.alias == endorser_alias:
        LOGGER.info(f"connection is with endorser...")
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

    LOGGER.info("< endorser_connections_event_handler")
