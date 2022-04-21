# https://github.com/hyperledger/aries-rfcs/blob/9127a964cfdba434b0ecdc8f95a794b98ecbf30d/features/0160-connection-protocol/README.md
import logging

from sqlalchemy import update

from acapy_client.api.connection_api import ConnectionApi
from api.api_client_utils import get_api_client
from api.core.config import settings
from api.core.event_bus import Event
from api.core.profile import Profile
from api.db.models.v1.contact import Contact
from api.endpoints.models.connections import ConnectionRoleType, ConnectionStateType
from api.endpoints.models.v1.contacts import ContactStatusType
from api.endpoints.models.webhooks import WEBHOOK_CONNECTIONS_LISTENER_PATTERN

logger = logging.getLogger(__name__)

connection_api = ConnectionApi(api_client=get_api_client())


async def inviter_flow(profile: Profile, payload: dict):
    logger.info(f"inviter_flow({profile.wallet_id}, {payload})")
    # for now, let's just update the state and status (maybe)...
    await update_contact(payload, profile)


async def invitee_flow(profile: Profile, payload: dict):
    logger.info(f"invitee_flow({profile.wallet_id}, {payload})")
    # for now, let's just update the state and status (maybe)...
    await update_contact(payload, profile)


async def update_contact(payload, profile):
    values = {"state": payload["state"]}
    if (
        payload["state"] == ConnectionStateType.completed
        or payload["state"] == ConnectionStateType.active
    ):
        values["status"] = ContactStatusType.active
    stmt = (
        update(Contact)
        .where(Contact.connection_id == payload["connection_id"])
        .values(values)
    )
    await profile.db.execute(stmt)
    await profile.db.commit()


async def handle_connection_events(profile: Profile, event: Event):
    payload = event.payload["payload"]
    their_role = payload["their_role"]

    if ConnectionRoleType.inviter == their_role:
        await inviter_flow(profile, payload)
    elif ConnectionRoleType.invitee == their_role:
        await invitee_flow(profile, payload)
    else:
        logger.info(
            f"unhandled connection event for their_role {their_role} = {payload}"
        )


def subscribe_event_listeners():
    settings.EVENT_BUS.subscribe(
        WEBHOOK_CONNECTIONS_LISTENER_PATTERN, handle_connection_events
    )
