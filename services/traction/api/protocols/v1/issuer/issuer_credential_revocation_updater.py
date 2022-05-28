from sqlalchemy import update

from api.core.profile import Profile
from api.db.models.v1.issuer import IssuerCredential
from api.db.session import async_session
from api.protocols.v1.issuer.issue_credential_protocol import (
    DefaultIssueCredentialProtocol,
)


class IssuerCredentialRevocationUpdater(DefaultIssueCredentialProtocol):
    def __init__(self):
        super().__init__()

    async def approve_for_processing(self, profile: Profile, payload: dict) -> bool:
        self.logger.info("> approve_for_processing()")
        has_issuer_credential = await super().approve_for_processing(profile, payload)
        has_revoc_reg_id = payload.get("revoc_reg_id") is not None
        approved = has_issuer_credential and has_revoc_reg_id
        self.logger.debug(f"has_issuer_credential = {has_issuer_credential}")
        self.logger.debug(f"has_revoc_reg_id = {has_revoc_reg_id}")
        self.logger.info(f"< approve_for_processing({approved})")
        return approved

    async def update_revocation_info(self, profile: Profile, payload: dict):
        self.logger.info("> update_revocation_info()")
        if payload.get("revoc_reg_id"):
            values = {
                "revoc_reg_id": payload.get("revoc_reg_id"),
                "revocation_id": payload.get("revocation_id"),
            }
            self.logger.debug(f"update values = {values}")
            stmt = (
                update(IssuerCredential)
                .where(IssuerCredential.tenant_id == profile.tenant_id)
                .where(
                    IssuerCredential.credential_exchange_id
                    == payload["credential_exchange_id"]
                )
                .values(values)
            )
            async with async_session() as db:
                await db.execute(stmt)
                await db.commit()
        self.logger.info("< update_revocation_info()")

    async def on_done(self, profile: Profile, payload: dict):
        self.logger.info("> on_done()")
        await self.update_revocation_info(profile, payload)
        self.logger.info("< on_done()")

    async def on_credential_acked(self, profile: Profile, payload: dict):
        self.logger.info("> on_credential_acked()")
        await self.update_revocation_info(profile, payload)
        self.logger.info("< on_credential_acked()")
