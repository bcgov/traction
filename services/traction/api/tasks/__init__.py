from .tasks import (
    SendSchemaRequestTask,
    SendCredentialOfferTask,
    SendCredDefRequestTask,
)


def subscribe_task_listeners():
    SendSchemaRequestTask()
    SendCredDefRequestTask()
    SendCredentialOfferTask()
