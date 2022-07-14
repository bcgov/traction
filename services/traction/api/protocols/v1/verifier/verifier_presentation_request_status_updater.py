from api.db.session import async_session
from api.endpoints.models.v1.errors import NotFoundError
from api.endpoints.models.v1.verifier import (
    VerifierPresentationStatusType,
    AcapyPresentProofStateType,
)

from .presentation_request_protocol import DefaultPresentationRequestProtocol

from api.core.profile import Profile
from api.db.models.v1.verifier_presentation import VerifierPresentation


class VerifierPresentationRequestStatusUpdater(DefaultPresentationRequestProtocol):
    def __init__(self):
        super().__init__()

    def get_presentation_exchange_id(self, payload: dict) -> str:
        try:
            return payload["presentation_exchange_id"]
        except KeyError:
            return None

    async def get_verifier_presentation(
        self, profile: Profile, payload: dict
    ) -> VerifierPresentation:
        pres_exch_id = self.get_presentation_exchange_id(payload=payload)
        try:
            async with async_session() as db:
                return await VerifierPresentation.get_by_pres_exch_id(
                    db, profile.tenant_id, pres_exch_id
                )
        except NotFoundError:
            return None

    async def approve_for_processing(self, profile: Profile, payload: dict) -> bool:
        self.logger.info("> approve_for_processing()")
        verifier_presentation = await self.get_verifier_presentation(profile, payload)
        has_record = verifier_presentation is not None
        approved = has_record
        self.logger.info(f"< approve_for_processing({approved})")
        return approved

    async def before_any(self, profile: Profile, payload: dict):
        self.logger.info("> before_any()")
        verifier_presentation = await self.get_verifier_presentation(profile, payload)

        values = {"state": payload["state"]}

        # what states should be marked as what status?
        verified_states = [AcapyPresentProofStateType.VERIFIED]
        received_states = [
            AcapyPresentProofStateType.PROPOSAL_RECEIVED,
            AcapyPresentProofStateType.PRESENTATION_RECEIVED,
        ]

        # what to do about abandoned?

        if payload["state"] in verified_states:
            values["status"] = VerifierPresentationStatusType.VERIFIED

        if payload["state"] in received_states:
            values["status"] = VerifierPresentationStatusType.RECEIVED

        self.logger.debug(f"update values = {values}")

        await VerifierPresentation.update_by_id(
            verifier_presentation.verifier_presentation_id, values
        )
        self.logger.info("< before_any()")
