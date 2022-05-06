import logging
from abc import ABC, abstractmethod

from api.core.config import settings
from api.core.event_bus import Event
from api.core.profile import Profile
from api.endpoints.models.connections import ConnectionStateType, ConnectionRoleType
from api.endpoints.models.webhooks import WEBHOOK_CONNECTIONS_LISTENER_PATTERN


def our_role(their_role: str):
    result = None
    if ConnectionRoleType.inviter == their_role:
        result = ConnectionRoleType.invitee
    elif ConnectionRoleType.invitee == their_role:
        result = ConnectionRoleType.inviter
    elif ConnectionRoleType.requester == their_role:
        result = ConnectionRoleType.responder
    elif ConnectionRoleType.responder == their_role:
        result = ConnectionRoleType.requester
    return result


def role_match(this_role: ConnectionRoleType, their_role: str):
    if not our_role:
        return True
    else:
        return this_role == our_role(their_role)


class ConnectionProtocol(ABC):
    def __init__(self, role: ConnectionRoleType | None = None):
        settings.EVENT_BUS.subscribe(WEBHOOK_CONNECTIONS_LISTENER_PATTERN, self.notify)
        self.role = role
        self.logger = logging.getLogger(type(self).__name__)

    async def notify(self, profile: Profile, event: Event):
        payload = event.payload["payload"]
        their_role = payload["their_role"]

        await self.before_all(profile=profile, payload=payload)

        if role_match(self.role, their_role):

            await self.before_any(profile=profile, payload=payload)

            if ConnectionStateType.start == payload["state"]:
                await self.on_start(profile=profile, payload=payload)
            elif ConnectionStateType.init == payload["state"]:
                await self.on_init(profile=profile, payload=payload)
            elif ConnectionStateType.invitation == payload["state"]:
                await self.on_invitation(profile=profile, payload=payload)
            elif ConnectionStateType.request == payload["state"]:
                await self.on_request(profile=profile, payload=payload)
            elif ConnectionStateType.response == payload["state"]:
                await self.on_response(profile=profile, payload=payload)
            elif ConnectionStateType.active == payload["state"]:
                await self.on_active(profile=profile, payload=payload)
            elif ConnectionStateType.completed == payload["state"]:
                await self.on_completed(profile=profile, payload=payload)
            elif ConnectionStateType.abandoned == payload["state"]:
                await self.on_abandoned(profile=profile, payload=payload)
            elif ConnectionStateType.error == payload["state"]:
                await self.on_error(profile=profile, payload=payload)
            else:
                pass

            await self.after_any(profile=profile, payload=payload)
        else:
            pass

        await self.after_all(profile=profile, payload=payload)

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
    async def on_start(self, profile: Profile, payload: dict):
        pass

    @abstractmethod
    async def on_init(self, profile: Profile, payload: dict):
        pass

    @abstractmethod
    async def on_invitation(self, profile: Profile, payload: dict):
        pass

    @abstractmethod
    async def on_request(self, profile: Profile, payload: dict):
        pass

    @abstractmethod
    async def on_response(self, profile: Profile, payload: dict):
        pass

    @abstractmethod
    async def on_active(self, profile: Profile, payload: dict):
        pass

    @abstractmethod
    async def on_completed(self, profile: Profile, payload: dict):
        pass

    @abstractmethod
    async def on_abandoned(self, profile: Profile, payload: dict):
        pass

    @abstractmethod
    async def on_error(self, profile: Profile, payload: dict):
        pass


class DefaultConnectionProtocol(ConnectionProtocol):
    async def before_all(self, profile: Profile, payload: dict):
        pass

    async def after_all(self, profile: Profile, payload: dict):
        pass

    async def before_any(self, profile: Profile, payload: dict):
        pass

    async def after_any(self, profile: Profile, payload: dict):
        pass

    async def on_start(self, profile: Profile, payload: dict):
        pass

    async def on_init(self, profile: Profile, payload: dict):
        pass

    async def on_invitation(self, profile: Profile, payload: dict):
        pass

    async def on_request(self, profile: Profile, payload: dict):
        pass

    async def on_response(self, profile: Profile, payload: dict):
        pass

    async def on_active(self, profile: Profile, payload: dict):
        pass

    async def on_completed(self, profile: Profile, payload: dict):
        pass

    async def on_abandoned(self, profile: Profile, payload: dict):
        pass

    async def on_error(self, profile: Profile, payload: dict):
        pass
