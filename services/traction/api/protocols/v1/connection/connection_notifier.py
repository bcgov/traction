import json

from api.core.profile import Profile
from api.endpoints.models.webhooks import TenantEventTopicType, TRACTION_EVENT_PREFIX
from api.protocols.v1.connection.connection_protocol import DefaultConnectionProtocol


class ConnectionNotifier(DefaultConnectionProtocol):
    def __init__(self):
        super().__init__(role=None)

    async def after_all(self, profile: Profile, payload: dict):
        self.logger.info("> after_all()")
        self.logger.debug(f"payload = {payload}")
        topic = TenantEventTopicType.connection
        event_topic = TRACTION_EVENT_PREFIX + topic
        self.logger.debug(f"profile.notify {event_topic}")

        payload = {
            "status": payload["state"],
            "role": payload["their_role"],
            "connection": json.dumps(payload),
        }

        await profile.notify(event_topic, {"topic": topic, "payload": payload})

        self.logger.info("< after_all()")
