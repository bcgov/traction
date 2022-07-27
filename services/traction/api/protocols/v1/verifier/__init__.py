from .verifier_presentation_proposol_handler import VerifierPresentationProposolHandler
from .verifier_presentation_request_status_updater import (
    VerifierPresentationRequestStatusUpdater,
)


def subscribe_present_proof_protocol_listeners():
    VerifierPresentationProposolHandler()
    VerifierPresentationRequestStatusUpdater()
