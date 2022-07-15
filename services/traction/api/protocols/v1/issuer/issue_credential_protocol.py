import logging
from abc import ABC, abstractmethod

from api.core.config import settings
from api.core.event_bus import Event
from api.core.profile import Profile
from api.db.models.v1.issuer import IssuerCredential
from api.db.session import async_session
from api.endpoints.models.credentials import CredentialRoleType, CredentialStateType
from api.endpoints.models.v1.errors import NotFoundError
from api.endpoints.models.webhooks import WEBHOOK_ISSUE_LISTENER_PATTERN


class IssueCredentialProtocol(ABC):
    def __init__(self):
        settings.EVENT_BUS.subscribe(WEBHOOK_ISSUE_LISTENER_PATTERN, self.notify)
        self.role = CredentialRoleType.issuer
        self._logger = logging.getLogger(type(self).__name__)

    @property
    def logger(self):
        return self._logger

    async def notify(self, profile: Profile, event: Event):
        self.logger.info("> notify()")
        payload = event.payload["payload"]
        self.logger.debug(f"payload={payload}")
        if self.role == payload["role"]:
            if "state" in payload:
                await self.before_all(profile=profile, payload=payload)

                if await self.approve_for_processing(profile=profile, payload=payload):
                    await self.before_any(profile=profile, payload=payload)
                    if CredentialStateType.pending == payload["state"]:
                        await self.on_pending(profile=profile, payload=payload)
                    elif CredentialStateType.proposal_received == payload["state"]:
                        await self.on_proposal_received(
                            profile=profile, payload=payload
                        )
                    elif CredentialStateType.offer_sent == payload["state"]:
                        await self.on_offer_sent(profile=profile, payload=payload)
                    elif CredentialStateType.offer_received == payload["state"]:
                        await self.on_offer_received(profile=profile, payload=payload)
                    elif CredentialStateType.request_received == payload["state"]:
                        await self.on_request_received(profile=profile, payload=payload)
                    elif CredentialStateType.request_sent == payload["state"]:
                        await self.on_request_sent(profile=profile, payload=payload)
                    elif CredentialStateType.credential_issued == payload["state"]:
                        await self.on_credential_issued(
                            profile=profile, payload=payload
                        )
                    elif CredentialStateType.credential_acked == payload["state"]:
                        await self.on_credential_acked(profile=profile, payload=payload)
                    elif CredentialStateType.credential_received == payload["state"]:
                        await self.on_credential_received(
                            profile=profile, payload=payload
                        )
                    elif CredentialStateType.done == payload["state"]:
                        await self.on_done(profile=profile, payload=payload)
                    elif CredentialStateType.abandoned == payload["state"]:
                        await self.on_abandoned(profile=profile, payload=payload)
                    elif CredentialStateType.error == payload["state"]:
                        await self.on_error(profile=profile, payload=payload)
                    elif CredentialStateType.credential_revoked == payload["state"]:
                        await self.on_credential_revoked(
                            profile=profile, payload=payload
                        )
                    else:
                        pass

                    await self.after_any(profile=profile, payload=payload)

                await self.after_all(profile=profile, payload=payload)
            else:
                # TODO: remove this when we update to acapy 7.4
                self.logger.info("payload has no key for 'state'")
                await self.on_unknown_state(profile=profile, payload=payload)
        self.logger.info("< notify()")

    # TODO: remove this when we update to acapy 7.4, workaround for bug in 7.3
    @abstractmethod
    async def on_unknown_state(self, profile: Profile, payload: dict):
        pass

    @abstractmethod
    def approve_for_processing(self, profile: Profile, payload: dict) -> bool:
        pass

    @abstractmethod
    async def before_all(self, profile: Profile, payload: dict):
        pass

    @abstractmethod
    async def after_all(self, profile: Profile, payload: dict):
        pass

    @abstractmethod
    async def before_any(self, profile: Profile, payload: dict):
        pass

    @abstractmethod
    async def after_any(self, profile: Profile, payload: dict):
        pass

    @abstractmethod
    async def on_pending(self, profile: Profile, payload: dict):
        pass

    @abstractmethod
    async def on_proposal_received(self, profile: Profile, payload: dict):
        pass

    @abstractmethod
    async def on_offer_received(self, profile: Profile, payload: dict):
        pass

    @abstractmethod
    async def on_offer_sent(self, profile: Profile, payload: dict):
        pass

    @abstractmethod
    async def on_request_received(self, profile: Profile, payload: dict):
        pass

    @abstractmethod
    async def on_request_sent(self, profile: Profile, payload: dict):
        pass

    @abstractmethod
    async def on_credential_issued(self, profile: Profile, payload: dict):
        pass

    @abstractmethod
    async def on_credential_acked(self, profile: Profile, payload: dict):
        pass

    @abstractmethod
    async def on_credential_received(self, profile: Profile, payload: dict):
        pass

    @abstractmethod
    async def on_done(self, profile: Profile, payload: dict):
        pass

    @abstractmethod
    async def on_abandoned(self, profile: Profile, payload: dict):
        pass

    @abstractmethod
    async def on_error(self, profile: Profile, payload: dict):
        pass

    @abstractmethod
    async def on_credential_revoked(self, profile: Profile, payload: dict):
        pass


class DefaultIssueCredentialProtocol(IssueCredentialProtocol):
    def __init__(self):
        super().__init__()

    def get_credential_exchange_id(self, payload: dict) -> str:
        try:
            return payload["credential_exchange_id"]
        except KeyError:
            return None

    async def get_issuer_credential(
        self, profile: Profile, payload: dict
    ) -> IssuerCredential:
        cred_ex_id = self.get_credential_exchange_id(payload=payload)
        try:
            async with async_session() as db:
                return await IssuerCredential.get_by_credential_exchange_id(
                    db, cred_ex_id
                )
        except NotFoundError:
            return None

    async def approve_for_processing(self, profile: Profile, payload: dict) -> bool:
        self.logger.info("> approve_for_processing()")
        issuer_credential = await self.get_issuer_credential(profile, payload)
        approved = issuer_credential is not None
        self.logger.info(f"< approve_for_processing({approved})")
        return approved

    # TODO: remove this when we update to acapy 7.4, workaround for bug in 7.3
    async def on_unknown_state(self, profile: Profile, payload: dict):
        pass

    async def before_all(self, profile: Profile, payload: dict):
        pass

    async def after_all(self, profile: Profile, payload: dict):
        pass

    async def before_any(self, profile: Profile, payload: dict):
        pass

    async def after_any(self, profile: Profile, payload: dict):
        pass

    async def on_pending(self, profile: Profile, payload: dict):
        pass

    async def on_proposal_received(self, profile: Profile, payload: dict):
        pass

    async def on_offer_received(self, profile: Profile, payload: dict):
        pass

    async def on_offer_sent(self, profile: Profile, payload: dict):
        pass

    async def on_request_received(self, profile: Profile, payload: dict):
        pass

    async def on_request_sent(self, profile: Profile, payload: dict):
        pass

    async def on_credential_issued(self, profile: Profile, payload: dict):
        pass

    async def on_credential_acked(self, profile: Profile, payload: dict):
        pass

    async def on_credential_received(self, profile: Profile, payload: dict):
        pass

    async def on_done(self, profile: Profile, payload: dict):
        pass

    async def on_abandoned(self, profile: Profile, payload: dict):
        pass

    async def on_error(self, profile: Profile, payload: dict):
        pass

    async def on_credential_revoked(self, profile: Profile, payload: dict):
        pass
