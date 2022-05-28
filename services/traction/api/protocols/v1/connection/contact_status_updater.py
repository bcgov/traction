from sqlalchemy import update

from api.core.profile import Profile
from api.db.models.v1.contact import Contact
from api.db.session import async_session
from api.endpoints.models.connections import ConnectionStateType
from api.endpoints.models.v1.contacts import ContactStatusType
from api.protocols.v1.connection.connection_protocol import DefaultConnectionProtocol


class ContactStatusUpdater(DefaultConnectionProtocol):
    def __init__(self):
        super().__init__(role=None)

    async def after_all(self, profile: Profile, payload: dict):
        self.logger.info("> after_all()")

        # response is included here for estatus
        # not all agents will send messages after they send response
        active_states = [
            ConnectionStateType.completed,
            ConnectionStateType.active,
            ConnectionStateType.response,
        ]

        values = {"state": payload["state"], "connection": payload}
        if payload["state"] in active_states:
            values["status"] = ContactStatusType.active
        self.logger.debug(f"update values = {values}")
        stmt = (
            update(Contact)
            .where(Contact.connection_id == payload["connection_id"])
            .values(values)
        )
        async with async_session() as db:
            await db.execute(stmt)
            await db.commit()
        self.logger.info("< after_all()")
