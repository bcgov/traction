from sqlalchemy import update

from api.core.profile import Profile
from api.db.models.v1.contact import Contact
from api.endpoints.models.connections import ConnectionStateType
from api.endpoints.models.v1.contacts import ContactStatusType
from api.protocols.v1.connection.connection_protocol import DefaultConnectionProtocol


class ContactStatusUpdater(DefaultConnectionProtocol):
    def __init__(self):
        super().__init__(role=None)

    async def after_all(self, profile: Profile, payload: dict):
        self.logger.info(f"after_all({profile.wallet_id}, {payload})")

        values = {"state": payload["state"]}
        if (
            payload["state"] == ConnectionStateType.completed
            or payload["state"] == ConnectionStateType.active
        ):
            values["status"] = ContactStatusType.active
            values["connection"] = payload
        stmt = (
            update(Contact)
            .where(Contact.connection_id == payload["connection_id"])
            .values(values)
        )
        await profile.db.execute(stmt)
        await profile.db.commit()
