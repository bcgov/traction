import uuid

from api.db.models.v1.contact import Contact
from api.db.session import async_session
from api.endpoints.models.v1.errors import NotFoundError
from api.endpoints.models.v1.verifier import (
    VerifierPresentationStatusType,
    AcapyPresentProofStateType,
)

from .presentation_request_protocol import DefaultPresentationRequestProtocol

from api.core.profile import Profile
from api.db.models.v1.verifier_presentation import VerifierPresentation


class VerifierPresentationProposolHandler(DefaultPresentationRequestProtocol):
    def __init__(self):
        super().__init__()

    def get_presentation_exchange_id(self, payload: dict) -> str:
        try:
            return payload["presentation_exchange_id"]
        except KeyError:
            return None

    async def get_contact(self, profile: Profile, payload: dict) -> Contact:
        connection_id = uuid.UUID(payload["connection_id"])
        try:
            async with async_session() as db:
                return await Contact.get_by_connection_id(
                    db, profile.tenant_id, connection_id=connection_id
                )
        except NotFoundError:
            return None

    async def approve_for_processing(self, profile: Profile, payload: dict) -> bool:
        self.logger.info("> approve_for_processing()")
        is_new_request = (
            payload["state"] in AcapyPresentProofStateType.PROPOSAL_RECEIVED
        )
        approved = is_new_request
        self.logger.info(f"is_new_request={is_new_request}")
        self.logger.info(f"< approve_for_processing({approved})")
        return approved

    async def on_proposal_received(self, profile: Profile, payload: dict):
        self.logger.info("> on_proposal_received()")
        # create a new verifier presentation!
        self.logger.info(f"@@@@@ payload = {payload}")
        contact = await self.get_contact(profile, payload)
        if contact:
            offer = VerifierPresentation(
                tenant_id=profile.tenant_id,
                contact_id=contact.contact_id,
                status=VerifierPresentationStatusType.PROPOSED,
                state=payload["state"],
                pres_exch_id=payload["presentation_exchange_id"],
            )
            async with async_session() as db:
                db.add(offer)
                await db.commit()

        # TODO: create payload and send notification to tenant.
        else:
            self.logger.warning(
                f"No contact found for connection_id<{payload['connection_id']}>, cannot create verifier presentation."  # noqa: E501
            )
        self.logger.info("< on_proposal_received()")
