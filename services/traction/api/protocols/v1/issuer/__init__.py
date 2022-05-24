from .issuer_credential_status_updater import IssuerCredentialStatusUpdater


def subscribe_issuer_protocol_listeners():
    IssuerCredentialStatusUpdater()
