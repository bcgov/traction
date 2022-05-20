from sqlalchemy import update

from api.core.profile import Profile
from api.db.models.v1.governance import CredentialTemplate
from api.endpoints.models.v1.errors import NotFoundError
from api.endpoints.models.v1.governance import TemplateStatusType
from api.protocols.v1.endorser.endorser_protocol import (
    DefaultEndorserProtocol,
    processing_states,
    cancelled_states,
)


class CreateCredDefProcessor(DefaultEndorserProtocol):
    def __init__(self):
        super().__init__()

    def get_schema_id(self, payload: dict) -> str:
        return payload["meta_data"]["context"]["schema_id"]

    def get_cred_def_id(self, payload: dict) -> str:
        return payload["meta_data"]["context"]["cred_def_id"]

    def get_transaction_id(self, payload: dict) -> str:
        return payload["transaction_id"]

    async def get_credential_template(
        self, profile: Profile, payload: dict
    ) -> CredentialTemplate:
        transaction_id = self.get_transaction_id(payload=payload)
        try:
            return await CredentialTemplate.get_by_transaction_id(
                profile.db, profile.tenant_id, transaction_id
            )
        except NotFoundError:
            return None

    def approve_for_processing(self, profile: Profile, payload: dict) -> bool:
        # check metadata for schema
        return (
            "schema_id" in payload["meta_data"]["context"]
            and "cred_def_id" in payload["meta_data"]["context"]
        )

    async def before_any(self, profile: Profile, payload: dict):
        o = await self.get_credential_template(profile, payload)
        schema_id = self.get_schema_id(payload)
        cred_def_id = self.get_cred_def_id(payload)

        if o:
            values = {
                "state": payload["state"],
                "cred_def_id": cred_def_id,
                "schema_id": schema_id,
            }

            await self.update_state(payload, profile, values, o)

    async def on_transaction_acked(self, profile: Profile, payload: dict):
        # set Status to Active if we are not allowing revocation
        # otherwise, the revocation processor will set active when appropriate
        o = await self.get_credential_template(profile, payload)
        if not o.revocation_enabled:
            await self.set_active(profile, o)

    async def update_state(self, payload, profile, values, item):
        if payload["state"] in processing_states:
            values["status"] = TemplateStatusType.in_progress
        if payload["state"] in cancelled_states:
            values["status"] = TemplateStatusType.cancelled
        stmt = (
            update(CredentialTemplate)
            .where(
                CredentialTemplate.credential_template_id == item.credential_template_id
            )
            .values(values)
        )
        await profile.db.execute(stmt)
        await profile.db.commit()

    async def set_active(self, profile, item):
        stmt = (
            update(CredentialTemplate)
            .where(
                CredentialTemplate.credential_template_id == item.credential_template_id
            )
            .values({"status": TemplateStatusType.active})
        )
        await profile.db.execute(stmt)
        await profile.db.commit()
