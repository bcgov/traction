from sqlalchemy import update

from api.core.profile import Profile
from api.db.models.v1.issuer import IssuedCredential
from api.endpoints.models.credentials import CredentialStateType
from api.endpoints.models.v1.issuer import IssuerCredentialStatusType
from api.protocols.v1.issuer.issue_credential_protocol import (
    DefaultIssueCredentialProtocol,
)


class IssuedCredentialStatusUpdater(DefaultIssueCredentialProtocol):
    def __init__(self):
        super().__init__()

    async def after_all(self, profile: Profile, payload: dict):
        self.logger.info(f"after_all({profile.wallet_id}, {payload})")

        values = {"state": payload["state"]}
        # TODO: determine Statuses
        if CredentialStateType.offer_sent == payload["state"]:
            values["status"] = IssuerCredentialStatusType.offer_sent

        stmt = (
            update(IssuedCredential)
            .where(IssuedCredential.tenant_id == profile.tenant_id)
            .where(
                IssuedCredential.credential_exchange_id
                == payload["credential_exchange_id"]
            )
            .values(values)
        )
        await profile.db.execute(stmt)
        await profile.db.commit()
