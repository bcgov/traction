import logging
import uuid
from abc import ABC, abstractmethod

from sqlalchemy import select

from api.core.config import settings
from api.core.event_bus import Event
from api.core.profile import Profile
from api.db.models import Tenant
from api.db.models.v1.contact import Contact
from api.db.models.v1.verifier_presentation import VerifierPresentation
from api.db.session import async_session
from api.endpoints.models.credentials import PresentationRoleType
from api.endpoints.models.v1.errors import NotFoundError
from api.endpoints.models.v1.verifier import AcapyPresentProofStateType
from api.endpoints.models.webhooks import WEBHOOK_PRESENT_LISTENER_PATTERN


class PresentationRequestProtocol(ABC):
    def __init__(self):
        settings.EVENT_BUS.subscribe(WEBHOOK_PRESENT_LISTENER_PATTERN, self.notify)
        self._logger = logging.getLogger(type(self).__name__)
        self.role = PresentationRoleType.verifier

    @property
    def logger(self):
        return self._logger

    async def notify(self, profile: Profile, event: Event):
        self.logger.info("> notify()")
        payload = event.payload["payload"]
        self.logger.debug(f"payload={payload}")
        self.logger.info(f"self.role={self.role} ? payload.role={payload['role']}")
        if self.role == payload["role"]:
            await self.before_all(profile=profile, payload=payload)

            if await self.approve_for_processing(profile=profile, payload=payload):
                await self.before_any(profile=profile, payload=payload)

                if AcapyPresentProofStateType.PROPOSAL_SENT == payload["state"]:
                    await self.on_proposal_sent(profile=profile, payload=payload)
                elif AcapyPresentProofStateType.PROPOSAL_RECEIVED == payload["state"]:
                    await self.on_proposal_received(profile=profile, payload=payload)
                elif AcapyPresentProofStateType.REQUEST_SENT == payload["state"]:
                    await self.on_request_sent(profile=profile, payload=payload)
                elif AcapyPresentProofStateType.REQUEST_RECEIVED == payload["state"]:
                    await self.on_request_received(profile=profile, payload=payload)
                elif AcapyPresentProofStateType.PRESENTATION_SENT == payload["state"]:
                    await self.on_presentation_sent(profile=profile, payload=payload)
                elif (
                    AcapyPresentProofStateType.PRESENTATION_RECEIVED == payload["state"]
                ):
                    await self.on_presentation_received(
                        profile=profile, payload=payload
                    )
                elif AcapyPresentProofStateType.VERIFIED == payload["state"]:
                    await self.on_verified(profile=profile, payload=payload)
                elif AcapyPresentProofStateType.PRESENTATION_ACKED == payload["state"]:
                    await self.on_presentation_acked(profile=profile, payload=payload)
                elif AcapyPresentProofStateType.ABANDONED == payload["state"]:
                    await self.on_abandoned(profile=profile, payload=payload)
                else:
                    pass

                await self.after_any(profile=profile, payload=payload)

            await self.after_all(profile=profile, payload=payload)
        self.logger.info("< notify()")

    async def get_tenant(self, profile: Profile) -> Tenant:
        async with async_session() as db:
            q = select(Tenant).where(Tenant.id == profile.tenant_id)
            q_result = await db.execute(q)
            db_rec = q_result.scalar_one_or_none()
            return db_rec

    def get_presentation_exchange_id(self, payload: dict) -> str:
        try:
            return payload["presentation_exchange_id"]
        except KeyError:
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

    @abstractmethod
    async def approve_for_processing(self, profile: Profile, payload: dict) -> bool:
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
    async def on_proposal_sent(self, profile: Profile, payload: dict):
        pass

    @abstractmethod
    async def on_proposal_received(self, profile: Profile, payload: dict):
        pass

    @abstractmethod
    async def on_request_sent(self, profile: Profile, payload: dict):
        pass

    @abstractmethod
    async def on_request_received(self, profile: Profile, payload: dict):
        pass

    @abstractmethod
    async def on_presentation_sent(self, profile: Profile, payload: dict):
        pass

    @abstractmethod
    async def on_presentation_received(self, profile: Profile, payload: dict):
        pass

    @abstractmethod
    async def on_verified(self, profile: Profile, payload: dict):
        pass

    @abstractmethod
    async def on_presentation_acked(self, profile: Profile, payload: dict):
        pass

    @abstractmethod
    async def on_abandoned(self, profile: Profile, payload: dict):
        pass


class DefaultPresentationRequestProtocol(PresentationRequestProtocol):
    def __init__(self):
        super().__init__()

    async def get_verifier_presentation(
        self, profile: Profile, payload: dict
    ) -> VerifierPresentation:
        pres_exch_id = self.get_presentation_exchange_id(payload=payload)
        try:
            async with async_session() as db:
                return await VerifierPresentation.get_by_pres_exch_id(
                    db, profile.tenant_id, pres_exch_id
                )
        except NotFoundError:
            return None

    async def approve_for_processing(self, profile: Profile, payload: dict) -> bool:
        pass

    async def before_all(self, profile: Profile, payload: dict):
        pass

    async def after_all(self, profile: Profile, payload: dict):
        pass

    async def before_any(self, profile: Profile, payload: dict):
        pass

    async def after_any(self, profile: Profile, payload: dict):
        pass

    async def on_proposal_sent(self, profile: Profile, payload: dict):
        pass

    async def on_proposal_received(self, profile: Profile, payload: dict):
        pass

    async def on_request_sent(self, profile: Profile, payload: dict):
        pass

    async def on_request_received(self, profile: Profile, payload: dict):
        pass

    async def on_presentation_sent(self, profile: Profile, payload: dict):
        pass

    async def on_presentation_received(self, profile: Profile, payload: dict):
        pass

    async def on_verified(self, profile: Profile, payload: dict):
        pass

    async def on_presentation_acked(self, profile: Profile, payload: dict):
        pass

    async def on_abandoned(self, profile: Profile, payload: dict):
        pass
