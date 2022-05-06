from api.protocols.v1.connection.contact_status_updater import ContactStatusUpdater
from api.protocols.v1.connection.reusable_invitation_processor import (
    ReusableInvitationProcessor,
)


def subscribe_connection_protocol_listeners():
    ReusableInvitationProcessor()
    ContactStatusUpdater()
