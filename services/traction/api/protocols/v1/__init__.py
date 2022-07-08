from .basic_messages import subscribe_basic_messages_protocol_listeners
from .connection import subscribe_connection_protocol_listeners
from .endorser import subscribe_endorser_protocol_listeners
from .holder import subscribe_holder_protocol_listeners
from .issuer import subscribe_issuer_protocol_listeners
from .revocation import subscribe_revocation_notification_protocol_listeners
from .verifier import subscribe_present_proof_protocol_listeners


def subscribe_protocol_listeners():
    subscribe_connection_protocol_listeners()
    subscribe_endorser_protocol_listeners()
    subscribe_issuer_protocol_listeners()
    subscribe_basic_messages_protocol_listeners()
    subscribe_present_proof_protocol_listeners()
    subscribe_revocation_notification_protocol_listeners()
    subscribe_holder_protocol_listeners()
