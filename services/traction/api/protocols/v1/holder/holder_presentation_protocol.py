import uuid

from api.core.profile import Profile
from api.db.models.v1.contact import Contact
from api.db.models.v1.holder import HolderPresentation
from api.db.session import async_session
from api.endpoints.models.credentials import PresentationRoleType
from api.endpoints.models.v1.errors import NotFoundError
from api.endpoints.models.v1.holder import HolderPresentationStatusType
from api.endpoints.models.v1.verifier import AcapyPresentProofStateType

from api.protocols.v1.verifier.presentation_request_protocol import (
    DefaultPresentationRequestProtocol,
)


class DefaultHolderPresentationProtocol(DefaultPresentationRequestProtocol):
    def __init__(self):
        super().__init__()
        self.role = PresentationRoleType.prover

    def get_presentation_exchange_id(self, payload: dict) -> str:
        try:
            return payload["presentation_exchange_id"]
        except KeyError:
            return None

    async def get_holder_presentation(
        self, profile: Profile, payload: dict
    ) -> HolderPresentation:
        pres_ex_id = self.get_presentation_exchange_id(payload=payload)
        try:
            async with async_session() as db:
                return await HolderPresentation.get_by_presentation_exchange_id(
                    db, pres_ex_id
                )
        except NotFoundError:
            return None

    async def get_contact(self, profile: Profile, payload: dict) -> Contact:
        connection_id = uuid.UUID(payload["connection_id"])
        try:
            async with async_session() as db:
                return await Contact.get_by_connection_id(
                    db, connection_id=connection_id
                )
        except NotFoundError:
            return None

    async def approve_for_processing(self, profile: Profile, payload: dict) -> bool:
        self.logger.info("> approve_for_processing()")
        holder_presentation = await self.get_holder_presentation(profile, payload)
        is_new_request = payload["state"] == AcapyPresentProofStateType.REQUEST_RECEIVED
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

            sent_states = [AcapyPresentProofStateType.PRESENTATION_SENT]

            accepted_states = [
                AcapyPresentProofStateType.PRESENTATION_ACKED,
            ]

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
        if contact:
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

    async def on_presentation_sent(self, profile: Profile, payload: dict):
        self.logger.info("> on_presentation_sent()")
        self.logger.info("< on_presentation_sent()")

    async def on_presentation_acked(self, profile: Profile, payload: dict):
        self.logger.info("> on_presentation_acked()")
        self.logger.info("< on_presentation_acked()")

    async def on_abandoned(self, profile: Profile, payload: dict):
        self.logger.info("> on_abandoned()")
        self.logger.info("< on_abandoned()")
