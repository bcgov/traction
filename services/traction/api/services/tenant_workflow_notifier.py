import logging

from sqlalchemy.ext.asyncio import AsyncSession

from api.core.profile import Profile
from api.db.models.tenant_issuer import TenantIssuerRead
from api.endpoints.models.webhooks import (
    TenantEventTopicType,
    TRACTION_EVENT_PREFIX,
)

logger = logging.getLogger(__name__)


class TenantWorkflowNotifier:
    def __init__(self, db: AsyncSession, *args, **kwargs) -> None:
        self._db: AsyncSession = db

    @property
    def db(self) -> AsyncSession:
        """Accessor for db session instance."""
        return self._db

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
