import logging
import re

from acapy_agent.core.event_bus import EventBus, Event
from acapy_agent.core.profile import Profile
from acapy_agent.protocols.issue_credential.v2_0.models.cred_ex_record import (
    V20CredExRecord,
)
from acapy_agent.revocation.models.issuer_cred_rev_record import IssuerCredRevRecord
from acapy_agent.storage.error import StorageNotFoundError

LOGGER = logging.getLogger(__name__)

# Subscribe to the event that's actually emitted by IssuerCredRevRecord
# Format: acapy::record::issuer_cred_rev::revoked
ISSUER_CRED_REV_REVOKED_EVENT_PATTERN = re.compile(
    r"^acapy::record::issuer_cred_rev::revoked$"
)


class IssuerRevocationService:
    def __init__(self):
        self._logger = logging.getLogger(__name__)

    async def update_credential_exchange_state(
        self, profile: Profile, rev_rec: IssuerCredRevRecord
    ) -> bool:
        """Update credential exchange record state to credential-revoked.

        Args:
            profile: The profile to use
            rev_rec: The IssuerCredRevRecord that was revoked

        Returns:
            bool: True if the state was updated, False otherwise
        """
        self._logger.info(
            f"> update_credential_exchange_state(cred_ex_id={rev_rec.cred_ex_id})"
        )

        if not rev_rec.cred_ex_id:
            self._logger.warning(
                "IssuerCredRevRecord has no cred_ex_id, cannot update credential exchange state"
            )
            return False

        updated = False
        try:
            async with profile.transaction() as txn:
                cred_ex_record = await V20CredExRecord.retrieve_by_id(
                    txn, rev_rec.cred_ex_id, for_update=True
                )
                cred_ex_record.state = V20CredExRecord.STATE_CREDENTIAL_REVOKED
                await cred_ex_record.save(txn, reason="revoke credential")
                await txn.commit()
                updated = True
                self._logger.info(
                    f"Updated credential exchange {rev_rec.cred_ex_id} state to credential-revoked"
                )
        except StorageNotFoundError:
            self._logger.warning(
                f"Credential exchange record not found for cred_ex_id: {rev_rec.cred_ex_id}"
            )
        except Exception as err:
            self._logger.error(
                f"Error updating credential exchange state for cred_ex_id {rev_rec.cred_ex_id}",
                exc_info=err,
            )

        self._logger.info(
            f"< update_credential_exchange_state(cred_ex_id={rev_rec.cred_ex_id}): updated={updated}"
        )
        return updated


def subscribe(bus: EventBus):
    """Subscribe to issuer credential revocation events."""
    bus.subscribe(ISSUER_CRED_REV_REVOKED_EVENT_PATTERN, issuer_cred_rev_revoked_handler)


async def issuer_cred_rev_revoked_handler(profile: Profile, event: Event):
    """Handle issuer credential revocation event.

    This handler is triggered when an IssuerCredRevRecord state changes to 'revoked'.
    It updates the corresponding credential exchange record state to 'credential-revoked'.
    """
    LOGGER.info(
        f"> issuer_cred_rev_revoked_handler: topic={event.topic}, payload_type={type(event.payload)}"
    )

    try:
        # The event payload is the serialized IssuerCredRevRecord (dict)
        # Deserialize it to get the IssuerCredRevRecord object
        LOGGER.debug(f"Event payload: {event.payload}")
        rev_rec = IssuerCredRevRecord.deserialize(event.payload)
        LOGGER.info(
            f"Deserialized IssuerCredRevRecord: cred_ex_id={rev_rec.cred_ex_id}, state={rev_rec.state}"
        )

        # Only process if cred_ex_id is present
        if rev_rec.cred_ex_id:
            srv = profile.inject(IssuerRevocationService)
            await srv.update_credential_exchange_state(profile, rev_rec)
        else:
            LOGGER.warning(
                "IssuerCredRevRecord has no cred_ex_id, skipping credential exchange update"
            )
    except Exception as err:
        LOGGER.error(
            "Error handling issuer credential revocation event", exc_info=err
        )

    LOGGER.info("< issuer_cred_rev_revoked_handler")
