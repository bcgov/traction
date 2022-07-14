import logging
from uuid import UUID

import dateutil

from api.core.config import settings
from api.core.event_bus import Event
from api.core.profile import Profile
from api.db.models import Tenant
from api.db.models.v1.contact import Contact
from api.db.models.v1.message import Message
from api.db.models.v1.tenant_configuration import (
    TenantConfiguration,
    TenantAutoResponseLog,
)
from api.db.session import async_session
from api.endpoints.models.v1.errors import NotFoundError
from api.endpoints.models.v1.messages import MessageStatusType, MessageRole
from api.endpoints.models.webhooks import WEBHOOK_BASICMESSAGES_LISTENER_PATTERN
from sqlalchemy import select
from starlette_context import context
from acapy_client.api.basicmessage_api import BasicmessageApi
from acapy_client.model.send_message import SendMessage
from api.api_client_utils import get_api_client
from api.services.v1 import tenant_configuration_service as config_service

basicmessage_api = BasicmessageApi(api_client=get_api_client())


class BasicMessagesProtocol:
    def __init__(self):
        settings.EVENT_BUS.subscribe(
            WEBHOOK_BASICMESSAGES_LISTENER_PATTERN, self.notify
        )
        self._logger = logging.getLogger(type(self).__name__)

    async def get_tenant(self, profile: Profile) -> Tenant:
        # TODO: refactor protocols to have a common listener and a common base class
        async with async_session() as db:
            q = select(Tenant).where(Tenant.id == profile.tenant_id)
            q_result = await db.execute(q)
            db_rec = q_result.scalar_one_or_none()
            return db_rec

    async def get_contact(self, tenant_id: str, connection_id: str) -> Contact:
        async with async_session() as db:
            try:
                return await Contact.get_by_connection_id(db, connection_id)
            except NotFoundError:
                self.logger.warning(
                    f"No contact found for connection_id<{connection_id}>"
                )
                return None

    async def get_tenant_configuration(self, tenant_id: UUID) -> TenantConfiguration:
        async with async_session() as db:
            return await TenantConfiguration.get_by_id(db, tenant_id)

    async def auto_response_exists(self, tenant_id: UUID, contact_id: UUID) -> bool:
        async with async_session() as db:
            rec = await TenantAutoResponseLog.get_from_tenant_to_contact(db, contact_id)
            return rec is not None

    async def log_auto_response(
        self, tenant_id: UUID, contact_id: UUID, message: str
    ) -> bool:
        async with async_session() as db:
            db_item = TenantAutoResponseLog(
                tenant_id=tenant_id,
                contact_id=contact_id,
                message=message,
            )
            db.add(db_item)
            await db.commit()

    @property
    def logger(self):
        return self._logger

    async def notify(self, profile: Profile, event: Event):
        self.logger.info("> notify()")
        payload = event.payload["payload"]
        self.logger.debug(f"payload={payload}")
        db_tenant = await self.get_tenant(profile)
        db_contact = await self.get_contact(profile.tenant_id, payload["connection_id"])
        if db_tenant and db_contact:
            # TODO: when we send notifications of messages, we want to send the content
            # across no matter what, however, we may not be storing the content.
            # The only way the tenant would see it is via a push notification/event.
            content = await config_service.stored_message_content(
                db_tenant.id, payload["content"]
            )
            async with async_session() as db:
                # there only one state (received)
                # for now just create a message for this tenant from the contact
                sent_time = dateutil.parser.parse(payload["sent_time"])
                db_item = Message(
                    message_id=payload["message_id"],
                    tenant_id=db_tenant.id,
                    contact_id=db_contact.contact_id,
                    status=MessageStatusType.received,
                    state=payload["state"],
                    role=MessageRole.recipient,
                    content=content,
                    sent_time=sent_time.replace(tzinfo=None),
                )
                db.add(db_item)
                await db.commit()

            # check if this tenant is set to auto respond and if so, send the response
            await self.auto_respond(db_tenant, db_contact)
        self.logger.info("< notify()")

    async def auto_respond(self, tenant: Tenant, contact: Contact):
        self.logger.debug("> auto_respond()")
        tenant_config = await self.get_tenant_configuration(tenant.id)
        if tenant_config.auto_respond_messages:
            response_exists = await self.auto_response_exists(
                tenant.id, contact.contact_id
            )
            if not response_exists:
                context["TENANT_WALLET_TOKEN"] = tenant.wallet_token
                content = (
                    tenant_config.auto_response_message
                    if tenant_config.auto_response_message
                    else f"'{tenant.name}' has received your message but does not correspond via messages"  # noqa: E501
                )

                body = SendMessage(content=content)
                basicmessage_api.connections_conn_id_send_message_post(
                    str(contact.connection_id), body=body
                )
                # now save that we sent an auto response to this connection
                await self.log_auto_response(tenant.id, contact.contact_id, content)
        self.logger.debug("< auto_respond()")
