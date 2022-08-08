import uuid

from api.core.profile import Profile
from api.db.models.v1.contact import Contact
from api.db.models.v1.holder import HolderCredential
from api.endpoints.models.v1.enumerated import CredentialRoleType, CredentialStateType
from api.endpoints.models.v1.errors import NotFoundError
from api.endpoints.models.v1.holder import HolderCredentialStatusType
from api.protocols.v1.issuer.issue_credential_protocol import IssueCredentialProtocol
from api.db.session import async_session


class DefaultHolderCredentialProtocol(IssueCredentialProtocol):
    def __init__(self):
        super().__init__()
        self.role = CredentialRoleType.holder

    def get_credential_exchange_id(self, payload: dict) -> str:
        try:
            return payload["credential_exchange_id"]
        except KeyError:
            return None

    async def get_holder_credential(
        self, profile: Profile, payload: dict
    ) -> HolderCredential:
        cred_ex_id = self.get_credential_exchange_id(payload=payload)
        try:
            async with async_session() as db:
                return await HolderCredential.get_by_credential_exchange_id(
                    db, profile.tenant_id, cred_ex_id
                )
        except NotFoundError:
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
        holder_credential = await self.get_holder_credential(profile, payload)
        is_new_offer = payload["state"] == CredentialStateType.offer_received
        is_existing_item = holder_credential is not None
        approved = is_new_offer or is_existing_item
        self.logger.debug(f"is_new_offer={is_new_offer}")
        self.logger.debug(f"is_existing_item={is_existing_item}")
        self.logger.info(f"< approve_for_processing({approved})")
        return approved

    async def before_all(self, profile: Profile, payload: dict):
        pass

    async def after_all(self, profile: Profile, payload: dict):
        pass

    async def before_any(self, profile: Profile, payload: dict):
        self.logger.info("> before_any()")
        # only update status if we've created the record
        item = await self.get_holder_credential(profile, payload)
        if item:
            self.logger.debug("holder credential exists, proceed with status update")
            values = {"state": payload["state"]}

            waiting_states = [CredentialStateType.request_sent]

            accepted_states = [
                CredentialStateType.credential_received,
                CredentialStateType.credential_acked,
            ]

            if payload["state"] in waiting_states:
                values["status"] = HolderCredentialStatusType.offer_accepted

            if payload["state"] in accepted_states:
                values["status"] = HolderCredentialStatusType.accepted

            self.logger.debug(f"update values = {values}")
            await HolderCredential.update_by_id(
                item_id=item.holder_credential_id, values=values
            )

        self.logger.info("< before_any()")

    async def after_any(self, profile: Profile, payload: dict):
        pass

    async def on_pending(self, profile: Profile, payload: dict):
        pass

    async def on_proposal_received(self, profile: Profile, payload: dict):
        pass

    async def on_offer_received(self, profile: Profile, payload: dict):
        self.logger.info("> on_offer_received()")
        # create a new holder credential!
        contact = await self.get_contact(profile, payload)
        if contact:
            offer = HolderCredential(
                tenant_id=profile.tenant_id,
                contact_id=contact.contact_id,
                status=HolderCredentialStatusType.offer_received,
                state=payload["state"],
                thread_id=payload["thread_id"],
                credential_exchange_id=payload["credential_exchange_id"],
                connection_id=payload["connection_id"],
                schema_id=payload["schema_id"],
                cred_def_id=payload["credential_definition_id"],
            )
            async with async_session() as db:
                db.add(offer)
                await db.commit()

        # TODO: create payload and send notification to tenant.
        else:
            self.logger.warning(
                f"No contact found for connection_id<{payload['connection_id']}>, cannot create holder credential."  # noqa: E501
            )
        self.logger.info("< on_offer_received()")

    async def on_offer_sent(self, profile: Profile, payload: dict):
        pass

    async def on_request_received(self, profile: Profile, payload: dict):
        pass

    async def on_request_sent(self, profile: Profile, payload: dict):
        self.logger.info("> on_request_sent()")
        self.logger.info("< on_request_sent()")

    async def on_credential_issued(self, profile: Profile, payload: dict):
        pass

    async def on_credential_acked(self, profile: Profile, payload: dict):
        self.logger.info("> on_credential_acked()")
        # update revocation ids if any, plus the wallet credential id
        item = await self.get_holder_credential(profile, payload)
        if item:
            self.logger.debug("holder credential exists, proceed with ack update")
            values = {"credential_id": payload["credential_id"]}

            if payload.get("revoc_reg_id"):
                values["revoc_reg_id"] = payload.get("revoc_reg_id")
                values["revocation_id"] = payload.get("revocation_id")

            self.logger.debug(f"update values = {values}")
            await HolderCredential.update_by_id(
                item_id=item.holder_credential_id, values=values
            )
        # TODO: send out notification ?
        self.logger.info("< on_credential_acked()")

    async def on_credential_received(self, profile: Profile, payload: dict):
        self.logger.info("> on_credential_received()")
        self.logger.info("< on_credential_received()")

    async def on_done(self, profile: Profile, payload: dict):
        pass

    async def on_abandoned(self, profile: Profile, payload: dict):
        pass

    async def on_error(self, profile: Profile, payload: dict):
        pass

    async def on_credential_revoked(self, profile: Profile, payload: dict):
        pass
