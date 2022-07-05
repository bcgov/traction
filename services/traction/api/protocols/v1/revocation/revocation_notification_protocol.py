import logging
from abc import ABC, abstractmethod

from api.core.config import settings
from api.core.event_bus import Event
from api.core.profile import Profile
from api.db.models.v1.issuer import IssuerCredential
from api.db.session import async_session
from api.endpoints.models.v1.errors import NotFoundError
from api.endpoints.models.v1.issuer import IssuerCredentialItem
from api.endpoints.models.webhooks import (
    WEBHOOK_REVOC_NOTIFY_LISTENER_PATTERN,
    TenantEventTopicType,
    TRACTION_EVENT_PREFIX,
)
from api.services.v1 import issuer_service


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

    async def get_issuer_credential(
        self, profile: Profile, revoc_reg_id: str, revocation_id: str
    ) -> IssuerCredentialItem:
        self.logger.info(f"> get_issuer_credential({revoc_reg_id},{revocation_id})")
        try:
            async with async_session() as db:
                rec = await IssuerCredential.get_by_revocation_ids(
                    db, revoc_reg_id, revocation_id
                )
                if rec:
                    self.logger.info(
                        f"issuer_credential_id = {rec.issuer_credential_id}"
                    )
                    result = await issuer_service.get_issuer_credential(
                        db,
                        rec.tenant_id,
                        None,
                        rec.issuer_credential_id,
                        True,
                    )
        except NotFoundError:
            self.logger.error("Error finding cred", exc_info=True)
            result = None
        self.logger.info(f"< get_issuer_credential(result = {result})")
        return result

    async def on_credential_revoked(self, profile: Profile, payload: dict):
        self.logger.info("> on_credential_revoked()")
        data = self.parse_payload(payload)
        self.logger.debug(f"parsed payload = {data}")
        # TODO: this is supposed to be for holder, but we aren't tracking that in v1
        # TODO: fix this when we track credentials for holder
        issuer_credential = await self.get_issuer_credential(
            profile, data["revoc_reg_id"], data["revocation_id"]
        )

        if issuer_credential:
            topic = TenantEventTopicType.issuer_cred_rev
            event_topic = TRACTION_EVENT_PREFIX + topic

            payload = {
                "status": "credential_revoked",
                "credential": issuer_credential.acapy.json(),
                "comment": data["comment"],
            }

            await profile.notify(event_topic, {"topic": topic, "payload": payload})

        self.logger.info("< on_credential_revoked()")
