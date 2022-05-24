from sqlalchemy import update

from api.core.profile import Profile
from api.db.models.v1.issuer import IssuerCredential
from api.protocols.v1.issuer.issue_credential_protocol import (
    DefaultIssueCredentialProtocol,
)


class IssuerCredentialRevocationUpdater(DefaultIssueCredentialProtocol):
    def __init__(self):
        super().__init__()

    async def approve_for_processing(self, profile: Profile, payload: dict) -> bool:
        approved = await super().approve_for_processing(profile, payload)
        return approved and payload.get("revoc_reg_id") is not None

    async def update_revocation_info(self, profile: Profile, payload: dict):
        if payload.get("revoc_reg_id"):
            values = {
                "revoc_reg_id": payload.get("revoc_reg_id"),
                "revocation_id": payload.get("revocation_id"),
            }
            stmt = (
                update(IssuerCredential)
                .where(IssuerCredential.tenant_id == profile.tenant_id)
                .where(
                    IssuerCredential.credential_exchange_id
                    == payload["credential_exchange_id"]
                )
                .values(values)
            )
            await profile.db.execute(stmt)
            await profile.db.commit()

    async def on_done(self, profile: Profile, payload: dict):
        return await self.update_revocation_info(profile, payload)

    async def on_credential_acked(self, profile: Profile, payload: dict):
        return await self.update_revocation_info(profile, payload)
