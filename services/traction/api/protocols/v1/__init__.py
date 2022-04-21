from api.protocols.v1 import connection_protocol


def subscribe_protocol_event_listeners():
    connection_protocol.subscribe_event_listeners()
