from .issued_credential_status_updater import IssuedCredentialStatusUpdater


def subscribe_issuer_protocol_listeners():
    IssuedCredentialStatusUpdater()
