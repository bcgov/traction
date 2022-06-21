from sqlalchemy import update
from api.db.session import async_session

from .present_proof_abc import DefaultPresentProofProtocol

from api.core.profile import Profile
from api.db.models.v1.verifier_presentation import VerifierPresentation
from api.endpoints.models.v1.verifier import AcapyPresentProofStateType


class VerifierPresentProofV10Protocol(DefaultPresentProofProtocol):
    def __init__(self):
        super().__init__()

    async def update_verifier_presentation(self, profile: Profile, payload: dict):
        self.logger.info("> update_verifier_presentation()")
        async with async_session() as db:
            vp = await VerifierPresentation.get_by_pres_exch_id(
                db, profile.tenant_id, payload["presentation_exchange_id"]
            )
            print(payload.keys())
            new_state = payload["presentation_exchange_id"]
            vp = await VerifierPresentation.update_by_id(
                vp.verifier_presentation_id, {"state": AcapyPresentProofStateType()}
            )

        self.logger.info("< update_revocation_info()")

    async def on_done(self, profile: Profile, payload: dict):
        self.logger.info("> on_done()")
        await self.update_revocation_info(profile, payload)
        self.logger.info("< on_done()")

    async def on_credential_acked(self, profile: Profile, payload: dict):
        self.logger.info("> on_credential_acked()")
        await self.update_revocation_info(profile, payload)
        self.logger.info("< on_credential_acked()")
