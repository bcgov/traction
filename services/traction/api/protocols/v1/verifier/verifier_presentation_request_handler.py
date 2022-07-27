from starlette_context import context

from api.db.session import async_session
from api.endpoints.models.v1.verifier import (
    VerifierPresentationStatusType,
    AcapyPresentProofStateType,
)
from api.services.v1.acapy_service import present_proof_api

from .presentation_request_protocol import DefaultPresentationRequestProtocol

from api.core.profile import Profile
from api.db.models.v1.verifier_presentation import VerifierPresentation


class VerifierPresentationRequestHandler(DefaultPresentationRequestProtocol):
    def __init__(self):
        super().__init__()

    async def approve_for_processing(self, profile: Profile, payload: dict) -> bool:
        self.logger.info("> approve_for_processing()")
        verifier_presentation = await self.get_verifier_presentation(profile, payload)
        has_record = verifier_presentation is not None
        approved = has_record
        self.logger.info(f"< approve_for_processing({approved})")
        return approved

    async def handle_abandoned(self, verifier_presentation, payload):
        if "error_msg" in payload:
            self.logger.debug(f"payload error_msg = {payload['error_msg']}")
            if str(payload["error_msg"]).startswith("abandoned"):
                self.logger.info("presentation request abandoned, request rejected.")
                values = {
                    "state": AcapyPresentProofStateType.ABANDONED,
                    "status": VerifierPresentationStatusType.REJECTED,
                }
                self.logger.debug(f"updating issuer credential = {values}")
                async with async_session() as db:
                    await VerifierPresentation.update_by_id(
                        verifier_presentation.verifier_presentation_id, values
                    )
                    await db.commit()

    async def on_request_sent(self, profile: Profile, payload: dict):
        self.logger.info("> on_request_sent()")
        verifier_presentation = await self.get_verifier_presentation(profile, payload)
        if verifier_presentation:
            #  update the proof request to match what was sent.
            values = {
                "proof_request": payload["presentation_request"],
                "name": payload["presentation_request"]["name"],
                "version": payload["presentation_request"]["version"],
            }
            async with async_session() as db:
                await VerifierPresentation.update_by_id(
                    verifier_presentation.verifier_presentation_id, values
                )
                await db.commit()

        self.logger.info("< on_request_sent()")

    async def on_presentation_received(self, profile: Profile, payload: dict):
        self.logger.info("> on_presentation_received()")
        self.logger.debug(f"payload['auto_verify'] {payload['auto_verify']}")
        if not payload["auto_verify"]:
            self.logger.info("presentation request is not auto verify... verify it.")
            verification_presentation = await self.get_verifier_presentation(
                profile, payload
            )
            if verification_presentation:
                # TODO: put this in a task when tasks refactored?
                tenant = await self.get_tenant(profile)
                context["TENANT_WALLET_TOKEN"] = tenant.wallet_token
                # need a check for from proposal...
                self.logger.info("call for verification")
                resp = present_proof_api.present_proof_records_pres_ex_id_verify_presentation_post(  # noqa:E501
                    str(verification_presentation.pres_exch_id)
                )
                self.logger.info(f"call for verification resp = {resp}")

        self.logger.info("< on_presentation_received()")
