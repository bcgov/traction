from api.protocols.v1.holder.holder_credential_protocol import (
    DefaultHolderCredentialProtocol,
)
from api.protocols.v1.holder.holder_presentation_protocol import (
    DefaultHolderPresentationProtocol,
)


def subscribe_holder_protocol_listeners():
    DefaultHolderCredentialProtocol()
    DefaultHolderPresentationProtocol()
