import json
import logging
from abc import ABC, abstractmethod

from api.core.config import settings
from api.core.event_bus import Event
from api.core.profile import Profile
from api.db.models.v1.holder import HolderCredential
from api.db.session import async_session
from api.endpoints.models.v1.errors import NotFoundError
from api.endpoints.models.v1.holder import HolderCredentialStatusType
from api.endpoints.models.webhooks import (
    WEBHOOK_REVOC_NOTIFY_LISTENER_PATTERN,
    TenantEventTopicType,
    TRACTION_EVENT_PREFIX,
)


class RevocationNotificationProtocol(ABC):
    def __init__(self):
        settings.EVENT_BUS.subscribe(WEBHOOK_REVOC_NOTIFY_LISTENER_PATTERN, self.notify)
        self._logger = logging.getLogger(type(self).__name__)

    @property
    def logger(self):
        return self._logger

    def parse_payload(self, payload: dict):
        comment = payload.get("comment")
        thread_id = payload.get("thread_id")
        # should be "indy::<rev_reg_id>::<cred_rev_id>"
        thread_id_parts = thread_id.split("::")
        revoc_reg_id = thread_id_parts[1]
        revocation_id = thread_id_parts[2]
        return {
            "thread_id": thread_id,
            "comment": comment,
            "revoc_reg_id": revoc_reg_id,
            "revocation_id": revocation_id,
        }

    async def notify(self, profile: Profile, event: Event):
        self.logger.info("> notify()")
        payload = event.payload["payload"]
        self.logger.debug(f"payload={payload}")
        await self.on_credential_revoked(profile, payload)
        self.logger.info("< notify()")

    @abstractmethod
    async def on_credential_revoked(self, profile: Profile, payload: dict):
        pass


class RevocationNotificationProcessor(RevocationNotificationProtocol):
    def __init__(self):
        super().__init__()

    async def get_holder_credential(
        self, profile: Profile, revoc_reg_id: str, revocation_id: str
    ) -> HolderCredential:
        self.logger.info(f"> get_holder_credential({revoc_reg_id},{revocation_id})")
        try:
            async with async_session() as db:
                return await HolderCredential.get_by_revocation_ids(
                    db, revoc_reg_id, revocation_id
                )
        except NotFoundError:
            self.logger.error("Error finding credential", exc_info=True)
            result = None
        self.logger.info(f"< get_holder_credential(result = {result})")
        return result

    async def update_holder_credential(
        self, item: HolderCredential, data: dict
    ) -> HolderCredential:
        values = {
            "revocation_comment": data["comment"],
            "revoked": True,
            "status": HolderCredentialStatusType.revoked,
        }
        return await HolderCredential.update_by_id(
            item_id=item.holder_credential_id, values=values
        )

    async def on_credential_revoked(self, profile: Profile, payload: dict):
        self.logger.info("> on_credential_revoked()")
        data = self.parse_payload(payload)
        self.logger.debug(f"parsed payload = {data}")
        item = await self.get_holder_credential(
            profile, data["revoc_reg_id"], data["revocation_id"]
        )

        if item:
            # update item to revoked!
            cred = await self.update_holder_credential(item, data)
            # TODO: what should this payload really contain?
            revocation_data = {
                "connection_id": cred.connection_id,
                "credential_exchange_id": cred.credential_exchange_id,
                "schema_id": cred.schema_id,
                "cred_def_id": cred.cred_def_id,
                "credential_id": cred.credential_id,
                "revoc_reg_id": cred.revoc_reg_id,
                "revocation_id": cred.revocation_id,
                "comment": cred.revocation_comment,
            }
            topic = TenantEventTopicType.issuer_cred_rev
            event_topic = TRACTION_EVENT_PREFIX + topic

            payload = {
                "status": "credential_revoked",
                "credential": json.dumps(revocation_data),
                "comment": data["comment"],
            }

            await profile.notify(event_topic, {"topic": topic, "payload": payload})

        self.logger.info("< on_credential_revoked()")
