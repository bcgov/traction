from .basic_messages import subscribe_basic_messages_protocol_listeners
from .connection import subscribe_connection_protocol_listeners
from .endorser import subscribe_endorser_protocol_listeners
from .issuer import subscribe_issuer_protocol_listeners


def subscribe_protocol_listeners():
    subscribe_connection_protocol_listeners()
    subscribe_endorser_protocol_listeners()
    subscribe_issuer_protocol_listeners()
    subscribe_basic_messages_protocol_listeners()
