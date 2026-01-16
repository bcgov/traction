import logging
import re

from acapy_agent.core.event_bus import EventBus, Event
from acapy_agent.core.profile import Profile
from acapy_agent.messaging.models.base import BaseModelError
from acapy_agent.protocols.issue_credential.v2_0.models.cred_ex_record import (
    V20CredExRecord,
)
from acapy_agent.protocols.issue_credential.v2_0.models.detail.indy import (
    V20CredExRecordIndy,
)
from acapy_agent.storage.error import StorageError, StorageNotFoundError

LOGGER = logging.getLogger(__name__)
REVOCATION_NOTIFICATION_EVENT_PATTERN = re.compile("acapy::revocation-notification::.*")


class HolderRevocationService:
    def __init__(self):
        self._logger = logging.getLogger(__name__)

    def parse_thread_id(self, thread_id: str):
        self._logger.info(f"> parse_thread_id({thread_id})")
        thread_id_parts = thread_id.split("::")
        revoc_reg_id = thread_id_parts[1]
        revocation_id = thread_id_parts[2]
        self._logger.info(f"< parse_thread_id() = `{revoc_reg_id}`, `{revocation_id}`")
        return revoc_reg_id, revocation_id

    async def find_credential_exchange_v20(
        self, profile, revoc_reg_id, revocation_id
    ) -> V20CredExRecord:
        self._logger.info(
            f"> find_credential_exchange_v20(revoc_reg_id={revoc_reg_id}, revocation_id={revocation_id})"
        )
        result = None
        tag_filter = {}
        post_filter = {"rev_reg_id": revoc_reg_id, "cred_rev_id": revocation_id}

        # there should be one and only one...
        # throw errors?
        try:
            async with profile.session() as session:
                # Query detail records to find cred_ex_id
                detail_records = await V20CredExRecordIndy.query(
                    session=session,
                    tag_filter=tag_filter,
                    post_filter_positive=post_filter,
                )
                if detail_records:
                    cred_ex_id = detail_records[0].cred_ex_id
                    # Retrieve the main credential exchange record
                    result = await V20CredExRecord.retrieve_by_id(session, cred_ex_id)
        except (StorageError, BaseModelError) as err:
            self._logger.warning("error finding credential exchange (v2.0)", err)
        self._logger.info(
            f"< find_credential_exchange_v20(revoc_reg_id={revoc_reg_id}, revocation_id={revocation_id}): {result is not None}"
        )
        return result

    async def set_credential_exchange_revoked_v20(
        self, profile, cred_ex_id, comment
    ) -> V20CredExRecord:
        self._logger.info(f"> set_credential_exchange_revoked_v20({cred_ex_id})")
        result = None
        revoked = False
        async with profile.transaction() as txn:
            try:
                result = await V20CredExRecord.retrieve_by_id(
                    txn, cred_ex_id, for_update=True
                )
                result.state = V20CredExRecord.STATE_CREDENTIAL_REVOKED
                result.error_msg = comment
                await result.save(txn, reason="revoke credential")
                await txn.commit()
                revoked = result.state == V20CredExRecord.STATE_CREDENTIAL_REVOKED
            except StorageNotFoundError as err:
                self._logger.warning(
                    "error finding or updating credential exchange (v2.0)", err
                )
        self._logger.info(
            f"< set_credential_exchange_revoked_v20({cred_ex_id}): revoked = {revoked}"
        )
        return result


def subscribe(bus: EventBus):
    bus.subscribe(
        REVOCATION_NOTIFICATION_EVENT_PATTERN, revocation_notification_handler
    )


async def revocation_notification_handler(profile: Profile, event: Event):
    LOGGER.info("> revocation_notification_handler")
    thread_id = event.payload["thread_id"]
    comment = event.payload["comment"]
    srv = profile.inject(HolderRevocationService)
    revoc_reg_id, revocation_id = srv.parse_thread_id(thread_id)
    # find it...
    record = await srv.find_credential_exchange_v20(
        profile, revoc_reg_id, revocation_id
    )
    if record:
        # mark as revoked...
        await srv.set_credential_exchange_revoked_v20(
            profile, record.cred_ex_id, comment
        )

    LOGGER.info("< revocation_notification_handler")
