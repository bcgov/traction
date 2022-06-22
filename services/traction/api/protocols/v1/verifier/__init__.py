from .verifier_presentation_request_status_updater import (
    VerifierPresentationRequestStatusUpdater,
)


def subscribe_present_proof_protocol_listeners():
    VerifierPresentationRequestStatusUpdater()
