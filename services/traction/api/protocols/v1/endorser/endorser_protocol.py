import logging
from abc import ABC, abstractmethod
from enum import Enum
from sqlalchemy import select

from api.core.config import settings
from api.core.event_bus import Event
from api.core.profile import Profile
from api.db.models import Tenant
from api.db.session import async_session
from api.endpoints.models.webhooks import WEBHOOK_ENDORSE_LISTENER_PATTERN


class EndorserStateType(str, Enum):
    init = "init"
    request_received = "request_received"
    request_sent = "request_sent"
    transaction_acked = "transaction_acked"
    transaction_cancelled = "transaction_cancelled"
    transaction_created = "transaction_created"
    transaction_endorsed = "transaction_endorsed"
    transaction_refused = "transaction_refused"
    transaction_resent = "transaction_resent"
    transaction_resent_received = "transaction_resent_received"


active_states = [EndorserStateType.transaction_acked]

processing_states = [
    EndorserStateType.request_sent,
    EndorserStateType.request_received,
    EndorserStateType.transaction_created,
    EndorserStateType.transaction_resent,
    EndorserStateType.transaction_resent_received,
    EndorserStateType.transaction_endorsed,
]

cancelled_states = [
    EndorserStateType.transaction_cancelled,
    EndorserStateType.transaction_refused,
]


class EndorserProtocol(ABC):
    def __init__(self):
        settings.EVENT_BUS.subscribe(WEBHOOK_ENDORSE_LISTENER_PATTERN, self.notify)
        self._logger = logging.getLogger(type(self).__name__)

    @property
    def logger(self):
        return self._logger

    async def notify(self, profile: Profile, event: Event):
        self.logger.info("> notify()")
        payload = event.payload["payload"]
        self.logger.debug(f"payload={payload}")

        await self.before_all(profile=profile, payload=payload)

        if await self.approve_for_processing(profile=profile, payload=payload):
            await self.before_any(profile=profile, payload=payload)

            if EndorserStateType.init == payload["state"]:
                await self.on_init(profile=profile, payload=payload)
            elif EndorserStateType.request_received == payload["state"]:
                await self.on_request_received(profile=profile, payload=payload)
            elif EndorserStateType.request_sent == payload["state"]:
                await self.on_request_sent(profile=profile, payload=payload)
            elif EndorserStateType.transaction_acked == payload["state"]:
                await self.on_transaction_acked(profile=profile, payload=payload)
            elif EndorserStateType.transaction_cancelled == payload["state"]:
                await self.on_transaction_cancelled(profile=profile, payload=payload)
            elif EndorserStateType.transaction_created == payload["state"]:
                await self.on_transaction_created(profile=profile, payload=payload)
            elif EndorserStateType.transaction_endorsed == payload["state"]:
                await self.on_transaction_endorsed(profile=profile, payload=payload)
            elif EndorserStateType.transaction_refused == payload["state"]:
                await self.on_transaction_refused(profile=profile, payload=payload)
            elif EndorserStateType.transaction_resent == payload["state"]:
                await self.on_transaction_resent(profile=profile, payload=payload)
            elif EndorserStateType.transaction_resent_received == payload["state"]:
                await self.on_transaction_resent_received(
                    profile=profile, payload=payload
                )
            else:
                pass

            await self.after_any(profile=profile, payload=payload)

        await self.after_all(profile=profile, payload=payload)
        self.logger.info("< notify()")

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
    async def on_init(self, profile: Profile, payload: dict):
        pass

    @abstractmethod
    async def on_request_received(self, profile: Profile, payload: dict):
        pass

    @abstractmethod
    async def on_request_sent(self, profile: Profile, payload: dict):
        pass

    @abstractmethod
    async def on_transaction_acked(self, profile: Profile, payload: dict):
        pass

    @abstractmethod
    async def on_transaction_cancelled(self, profile: Profile, payload: dict):
        pass

    @abstractmethod
    async def on_transaction_created(self, profile: Profile, payload: dict):
        pass

    @abstractmethod
    async def on_transaction_endorsed(self, profile: Profile, payload: dict):
        pass

    @abstractmethod
    async def on_transaction_refused(self, profile: Profile, payload: dict):
        pass

    @abstractmethod
    async def on_transaction_resent(self, profile: Profile, payload: dict):
        pass

    @abstractmethod
    async def on_transaction_resent_received(self, profile: Profile, payload: dict):
        pass


class DefaultEndorserProtocol(EndorserProtocol):
    async def get_tenant(self, profile: Profile) -> Tenant:
        async with async_session() as db:
            q = select(Tenant).where(Tenant.id == profile.tenant_id)
            q_result = await db.execute(q)
            db_rec = q_result.scalar_one_or_none()
            return db_rec

    async def approve_for_processing(self, profile: Profile, payload: dict) -> bool:
        return False

    async def before_all(self, profile: Profile, payload: dict):
        pass

    async def after_all(self, profile: Profile, payload: dict):
        pass

    async def before_any(self, profile: Profile, payload: dict):
        pass

    async def after_any(self, profile: Profile, payload: dict):
        pass

    async def on_init(self, profile: Profile, payload: dict):
        pass

    async def on_request_received(self, profile: Profile, payload: dict):
        pass

    async def on_request_sent(self, profile: Profile, payload: dict):
        pass

    async def on_transaction_acked(self, profile: Profile, payload: dict):
        pass

    async def on_transaction_cancelled(self, profile: Profile, payload: dict):
        pass

    async def on_transaction_created(self, profile: Profile, payload: dict):
        pass

    async def on_transaction_endorsed(self, profile: Profile, payload: dict):
        pass

    async def on_transaction_refused(self, profile: Profile, payload: dict):
        pass

    async def on_transaction_resent(self, profile: Profile, payload: dict):
        pass

    async def on_transaction_resent_received(self, profile: Profile, payload: dict):
        pass
