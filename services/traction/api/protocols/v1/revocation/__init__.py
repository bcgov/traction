from api.protocols.v1.revocation.revocation_notification_protocol import (
    RevocationNotificationProcessor,
)


def subscribe_revocation_notification_protocol_listeners():
    RevocationNotificationProcessor()
