import logging

from sqlalchemy.ext.asyncio import AsyncSession

from api.core.profile import Profile
from api.db.models.tenant_issuer import TenantIssuerRead
from api.db.models.tenant_schema import TenantSchemaRead
from api.endpoints.models.webhooks import (
    TenantEventTopicType,
    TRACTION_EVENT_PREFIX,
)
from api.db.models.issue_credential import (
    IssueCredentialRead,
)

logger = logging.getLogger(__name__)


class TenantWorkflowNotifier:
    def __init__(self, db: AsyncSession, *args, **kwargs) -> None:
        self._db: AsyncSession = db

    @property
    def db(self) -> AsyncSession:
        """Accessor for db session instance."""
        return self._db

    async def issuer_workflow_cred_revoc(
        self, cred_info: IssueCredentialRead, comment: str
    ):
        logger.info("received cred revoc")
        # emit an event for any interested listeners
        profile = Profile(cred_info.wallet_id, cred_info.tenant_id, self.db)
        topic = TenantEventTopicType.issuer_cred_rev
        event_topic = TRACTION_EVENT_PREFIX + topic
        logger.info(f"profile.notify {event_topic}")

        # TODO: Webhook payload schema's should become pydantic models?
        payload = {
            "status": "credential_revoked",
            "credential": cred_info.json(),
            "cred_issue_id": str(cred_info.id),
            "comment": comment,
        }

        await profile.notify(event_topic, {"topic": topic, "payload": payload})

    async def issuer_workflow_completed(self, tenant_issuer: TenantIssuerRead):
        logger.info("issuer workflow complete")
        # emit an event for any interested listeners
        profile = Profile(tenant_issuer.wallet_id, tenant_issuer.tenant_id, self.db)
        topic = TenantEventTopicType.issuer
        event_topic = TRACTION_EVENT_PREFIX + topic
        logger.info(f"profile.notify {event_topic}")
        # TODO: what should be in this payload?
        payload = {
            "status": "completed",
            "public_did": tenant_issuer.public_did,
            "public_did_state": tenant_issuer.public_did_state,
        }

        await profile.notify(event_topic, {"topic": topic, "payload": payload})

    async def schema_workflow_completed(self, tenant_schema: TenantSchemaRead):
        logger.info("schema workflow complete")
        # emit an event for any interested listeners
        profile = Profile(tenant_schema.wallet_id, tenant_schema.tenant_id, self.db)
        topic = TenantEventTopicType.schema
        event_topic = TRACTION_EVENT_PREFIX + topic
        logger.info(f"profile.notify {event_topic}")
        # TODO: what should be in this payload?
        payload = {
            "status": "completed",
            "schema_id": tenant_schema.schema_id,
            "cred_def_id": tenant_schema.cred_def_id,
            "cred_def_state": tenant_schema.cred_def_state,
            "cred_def_tag": tenant_schema.cred_def_tag,
        }

        await profile.notify(event_topic, {"topic": topic, "payload": payload})
