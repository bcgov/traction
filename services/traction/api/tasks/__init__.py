from .tasks import (
    SendSchemaRequestTask,
    SendCredentialOfferTask,
    SendCredDefRequestTask,
)
from .present_proof_tasks import SendPresentProofTask


def subscribe_task_listeners():
    SendSchemaRequestTask()
    SendCredDefRequestTask()
    SendCredentialOfferTask()
    SendPresentProofTask()
