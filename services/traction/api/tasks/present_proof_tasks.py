import logging
from re import Pattern, compile
from enum import Enum
from uuid import UUID

from api.tasks.tasks import Task, TractionTaskType
from api.db.models import Tenant

TRACTION_TASK_PREFIX = "traction::TASK::"


TRACTION_SEND_PRESENT_PROOF_REQ_PATTERN = compile(
    f"^{TRACTION_TASK_PREFIX}{TractionTaskType.send_present_proof_req}(.*)?$"
)


def get_logger(cls):
    return logging.getLogger(cls.__name__)


class SendPresentProofTask(Task):
    @staticmethod
    def _listener_pattern() -> Pattern[str]:
        return TRACTION_SEND_PRESENT_PROOF_REQ_PATTERN

    @staticmethod
    def _event_topic() -> str:
        return TRACTION_TASK_PREFIX + TractionTaskType.send_present_proof_req

    async def _perform_task(self, tenant: Tenant, payload: dict):
        self.logger.info("> _perform_task()")
        self.logger.warn("NOT IMPLEMENTED")

        # call acapy

        pass

    @classmethod
    async def assign(
        cls,
        tenant_id: UUID,
        wallet_id: UUID,
        proof_request: object,
        contact_id: UUID,
    ):
        get_logger(cls).info("> _assign()")
        get_logger(cls).debug(f"tenant_id = {tenant_id}")
        get_logger(cls).debug(f"wallet_id = {wallet_id}")
        get_logger(cls).debug(f"contact_id = {contact_id}, payload = {proof_request}")
        get_logger(cls).warn(f"NOT IMPLEMENTED")

        payload = {"contact_id": contact_id, "proof_request": proof_request}

        await cls._assign(tenant_id, wallet_id, payload)
        pass
