import logging
import re

from acapy_agent.core.event_bus import EventBus, Event
from acapy_agent.core.profile import Profile
from acapy_agent.messaging.models.base import BaseModelError
from acapy_agent.protocols.issue_credential.v1_0 import V10CredentialExchange
from acapy_agent.storage.error import StorageError, StorageNotFoundError

LOGGER = logging.getLogger(__name__)
REVOCATION_NOTIFICATION_EVENT_PATTERN = re.compile(
    f"acapy::revocation-notification::.*"
)


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

    async def find_credential_exchange_v10(
        self, profile, revoc_reg_id, revocation_id
    ) -> V10CredentialExchange:
        self._logger.info(
            f"> find_credential_exchange_v10(revoc_reg_id={revoc_reg_id}, revocation_id={revocation_id})"
        )
        result = None
        tag_filter = {}
        post_filter = {"revoc_reg_id": revoc_reg_id, "revocation_id": revocation_id}

        # there should be one and only one...
        # throw errors?
        try:
            async with profile.session() as session:
                records = await V10CredentialExchange.query(
                    session=session,
                    tag_filter=tag_filter,
                    post_filter_positive=post_filter,
                )
                result = records[0]
        except (StorageError, BaseModelError) as err:
            self._logger.warning("error finding credential exchange (v1.0)", err)
        self._logger.info(
            f"< find_credential_exchange_v10(revoc_reg_id={revoc_reg_id}, revocation_id={revocation_id}): {result is not None}"
        )
        return result

    async def set_credential_exchange_revoked_v10(
        self, profile, credential_exchange_id, comment
    ) -> V10CredentialExchange:
        self._logger.info(
            f"> set_credential_exchange_revoked_v10({credential_exchange_id})"
        )
        result = None
        revoked = False
        async with profile.transaction() as txn:
            try:
                result = await V10CredentialExchange.retrieve_by_id(
                    txn, credential_exchange_id, for_update=True
                )
                result.state = V10CredentialExchange.STATE_CREDENTIAL_REVOKED
                result.error_msg = comment
                await result.save(txn, reason="revoke credential")
                await txn.commit()
                revoked = result.state == V10CredentialExchange.STATE_CREDENTIAL_REVOKED
            except StorageNotFoundError as err:
                self._logger.warning(
                    "error finding or updating credential exchange (v1.0)", err
                )
        self._logger.info(
            f"< set_credential_exchange_revoked_v10({credential_exchange_id}): revoked = {revoked}"
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
    record = await srv.find_credential_exchange_v10(
        profile, revoc_reg_id, revocation_id
    )
    if record:
        # mark as revoked...
        await srv.set_credential_exchange_revoked_v10(
            profile, record.credential_exchange_id, comment
        )

    LOGGER.info("< revocation_notification_handler")
