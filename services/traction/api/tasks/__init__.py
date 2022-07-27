from .tasks import (
    SendSchemaRequestTask,
    SendCredentialOfferTask,
    SendCredDefRequestTask,
)
from .present_proof_tasks import SendPresentProofTask
from .public_did_task import RegisterPublicDIDTask


def subscribe_task_listeners():
    SendSchemaRequestTask()
    SendCredDefRequestTask()
    SendCredentialOfferTask()
    SendPresentProofTask()
    RegisterPublicDIDTask()
