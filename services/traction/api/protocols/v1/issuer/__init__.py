from .issuer_credential_revocation_updater import IssuerCredentialRevocationUpdater
from .issuer_credential_status_updater import IssuerCredentialStatusUpdater


def subscribe_issuer_protocol_listeners():
    IssuerCredentialStatusUpdater()
    IssuerCredentialRevocationUpdater()
