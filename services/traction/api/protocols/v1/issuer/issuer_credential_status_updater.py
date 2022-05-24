from sqlalchemy import update

from api.core.profile import Profile
from api.db.models.v1.issuer import IssuerCredential
from api.endpoints.models.credentials import CredentialStateType
from api.endpoints.models.v1.issuer import IssuerCredentialStatusType
from api.protocols.v1.issuer.issue_credential_protocol import (
    DefaultIssueCredentialProtocol,
)


class IssuerCredentialStatusUpdater(DefaultIssueCredentialProtocol):
    def __init__(self):
        super().__init__()

    async def before_any(self, profile: Profile, payload: dict):
        self.logger.debug(f"before_any({profile.wallet_id}, {payload})")

        values = {"state": payload["state"]}

        offered_states = [
            CredentialStateType.offer_sent,
            CredentialStateType.request_received,
        ]

        issued_states = [
            CredentialStateType.credential_issued,
            CredentialStateType.credential_acked,
        ]

        if payload["state"] in offered_states:
            values["status"] = IssuerCredentialStatusType.offer_sent

        if payload["state"] in issued_states:
            values["status"] = IssuerCredentialStatusType.issued

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
