import logging

import dateutil

from api.core.config import settings
from api.core.event_bus import Event
from api.core.profile import Profile
from api.db.models.v1.contact import Contact
from api.db.models.v1.message import Message
from api.db.session import async_session
from api.endpoints.models.v1.messages import MessageStatusType, MessageRole
from api.endpoints.models.webhooks import WEBHOOK_BASICMESSAGES_LISTENER_PATTERN


class BasicMessagesProtocol:
    def __init__(self):
        settings.EVENT_BUS.subscribe(
            WEBHOOK_BASICMESSAGES_LISTENER_PATTERN, self.notify
        )
        self._logger = logging.getLogger(type(self).__name__)

    @property
    def logger(self):
        return self._logger

    async def notify(self, profile: Profile, event: Event):
        self.logger.info("> notify()")
        payload = event.payload["payload"]
        self.logger.debug(f"payload={payload}")
        # there only one state (received)
        # for now just create a message for this tenant from the connection/contact
        sent_time = dateutil.parser.parse(payload["sent_time"])
        async with async_session() as db:
            db_contact = await Contact.get_by_connection_id(
                db, profile.tenant_id, payload["connection_id"]
            )
            db_item = Message(
                message_id=payload["message_id"],
                tenant_id=profile.tenant_id,
                contact_id=db_contact.contact_id,
                status=MessageStatusType.received,
                state=payload["state"],
                role=MessageRole.recipient,
                content=payload["content"],
                sent_time=sent_time.replace(tzinfo=None),
            )
            db.add(db_item)
            await db.commit()

        self.logger.info("< notify()")
