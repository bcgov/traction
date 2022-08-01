from api.protocols.v1.connection.connection_notifier import (
    ConnectionNotifier,
)
from api.protocols.v1.connection.contact_status_updater import ContactStatusUpdater
from api.protocols.v1.connection.endorser_connection_processor import (
    EndorserConnectionProcessor,
)
from api.protocols.v1.connection.multi_use_invitation_processor import (
    MultiUseInvitationProcessor,
)


def subscribe_connection_protocol_listeners():
    MultiUseInvitationProcessor()
    ContactStatusUpdater()
    ConnectionNotifier()
    EndorserConnectionProcessor()
