from api.core.profile import Profile
from api.db.models.v1.holder import HolderPresentation
from api.db.session import async_session
from api.endpoints.models.credentials import PresentationRoleType
from api.endpoints.models.v1.errors import NotFoundError
from api.endpoints.models.v1.holder import HolderPresentationStatusType
from api.endpoints.models.v1.verifier import AcapyPresentProofStateType

from api.protocols.v1.verifier.presentation_request_protocol import (
    DefaultPresentationRequestProtocol,
)

new_request_states = [
    AcapyPresentProofStateType.REQUEST_RECEIVED,
]


class DefaultHolderPresentationProtocol(DefaultPresentationRequestProtocol):
    def __init__(self):
        super().__init__()
        self.role = PresentationRoleType.prover

    async def get_holder_presentation(
        self, profile: Profile, payload: dict
    ) -> HolderPresentation:
        pres_ex_id = self.get_presentation_exchange_id(payload=payload)
        try:
            async with async_session() as db:
                return await HolderPresentation.get_by_presentation_exchange_id(
                    db, profile.tenant_id, pres_ex_id
                )
        except NotFoundError:
            return None

    async def approve_for_processing(self, profile: Profile, payload: dict) -> bool:
        self.logger.info("> approve_for_processing()")
        holder_presentation = await self.get_holder_presentation(profile, payload)
        is_new_request = payload["state"] in new_request_states
        is_existing_item = holder_presentation is not None
        approved = is_new_request or is_existing_item
        self.logger.info(f"is_new_request={is_new_request}")
        self.logger.info(f"is_existing_item={is_existing_item}")
        self.logger.info(f"< approve_for_processing({approved})")
        return approved

    async def before_any(self, profile: Profile, payload: dict):
        self.logger.info("> before_any()")
        # only update status if we've created the record
        item = await self.get_holder_presentation(profile, payload)
        if item:
            self.logger.debug("holder presentation exists, proceed with status update")
            values = {"state": payload["state"]}

            proposal_states = [
                AcapyPresentProofStateType.PROPOSAL_SENT,
            ]
            sent_states = [AcapyPresentProofStateType.PRESENTATION_SENT]

            accepted_states = [
                AcapyPresentProofStateType.PRESENTATION_ACKED,
            ]

            if payload["state"] in proposal_states:
                values["status"] = HolderPresentationStatusType.proposol_sent

            if payload["state"] in sent_states:
                values["status"] = HolderPresentationStatusType.presentation_sent

            if payload["state"] in accepted_states:
                values["status"] = HolderPresentationStatusType.presentation_acked

            self.logger.debug(f"update values = {values}")
            await HolderPresentation.update_by_id(
                item_id=item.holder_presentation_id, values=values
            )

        self.logger.info("< before_any()")

    async def on_request_received(self, profile: Profile, payload: dict):
        self.logger.info("> on_request_received()")
        # create a new holder credential!
        contact = await self.get_contact(profile, payload)
        holder_presentation = await self.get_holder_presentation(profile, payload)
        if contact:
            if holder_presentation:
                # may have one due to a sent proposal
                values = {
                    "status": HolderPresentationStatusType.request_received,
                    "state": payload["state"],
                }
                await HolderPresentation.update_by_id(
                    item_id=holder_presentation.holder_presentation_id, values=values
                )
            else:
                offer = HolderPresentation(
                    tenant_id=profile.tenant_id,
                    contact_id=contact.contact_id,
                    status=HolderPresentationStatusType.request_received,
                    state=payload["state"],
                    thread_id=payload["thread_id"],
                    presentation_exchange_id=payload["presentation_exchange_id"],
                    connection_id=payload["connection_id"],
                )
                async with async_session() as db:
                    db.add(offer)
                    await db.commit()

        # TODO: create payload and send notification to tenant.
        else:
            self.logger.warning(
                f"No contact found for connection_id<{payload['connection_id']}>, cannot create holder presentation."  # noqa: E501
            )
        self.logger.info("< on_request_received()")
