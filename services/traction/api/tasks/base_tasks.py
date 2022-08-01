import logging
import re
from abc import ABC, abstractmethod
from enum import Enum
from re import Pattern
from uuid import UUID

from sqlalchemy import select
from starlette_context import context

from api.core.config import settings
from api.core.event_bus import Event
from api.core.profile import Profile
from api.db.models import Tenant
from api.db.session import async_session


class TractionTaskType(str, Enum):
    send_schema_request = "send_schema_request"
    send_cred_def_request = "send_cred_def_request"
    send_credential_offer = "send_credential_offer"
    send_present_proof_req = "send_present_proof_req"
    register_public_did = "register_public_did"


TRACTION_TASK_PREFIX = "traction::TASK::"
TRACTION_TASK_LISTENER_PATTERN = re.compile(f"^{TRACTION_TASK_PREFIX}(.*)?$")

TRACTION_SEND_SCHEMA_REQUEST_LISTENER_PATTERN = re.compile(
    f"^{TRACTION_TASK_PREFIX}{TractionTaskType.send_schema_request}(.*)?$"
)

TRACTION_SEND_CRED_DEF_REQUEST_LISTENER_PATTERN = re.compile(
    f"^{TRACTION_TASK_PREFIX}{TractionTaskType.send_cred_def_request}(.*)?$"
)

TRACTION_SEND_CREDENTIAL_OFFER_LISTENER_PATTERN = re.compile(
    f"^{TRACTION_TASK_PREFIX}{TractionTaskType.send_credential_offer}(.*)?$"
)

TRACTION_SEND_PRESENT_PROOF_REQ_PATTERN = re.compile(
    f"^{TRACTION_TASK_PREFIX}{TractionTaskType.send_present_proof_req}(.*)?$"
)

TRACTION_REGISTER_PUBLIC_DID_PATTERN = re.compile(
    f"^{TRACTION_TASK_PREFIX}{TractionTaskType.register_public_did}(.*)?$"
)


def get_logger(cls):
    return logging.getLogger(cls.__name__)


class Task(ABC):
    """Task (Abstract).

    The Task class is for offloading work to the event bus. There are many long running
    actions in AcaPy/Ledger etc. Use tasks to perform background work. In general, these
     tasks will call AcaPy or the ledger and the flow will be handled in protocol
    listeners as the conversations flow between the various states. Tasks will be the
    kickoff/starting point of those conversations.

    Implementing classes will specify the event bus topics and listener pattern and
    will implement the actual work (_perform_task).

    Implementing classes should create a specific class method to trigger the work.
    These methods should build the payload and call _assign (which places the task on
    the event bus).

    In this way, the Task class can provide an easy way for callers to assign the task
    to the event bus and do the work once it comes off the bus.

    To facilitate calls to AcaPy, the tenant's wallet token is added to the context
    before _perform_task is called.

    Although the event profile contains a db session object, do NOT use this. Open a
    session in _perform_task if/when needed.

    Implementing classes will need to be referenced by a task_listener, found in tasks/
    __init__.py for the default
    """

    def __init__(self):
        self._logger = logging.getLogger(type(self).__name__)
        self._pattern = self._listener_pattern()
        settings.EVENT_BUS.subscribe(self._pattern, self._notify)

    @staticmethod
    @abstractmethod
    def _listener_pattern() -> Pattern[str]:
        pass

    @staticmethod
    @abstractmethod
    def _event_topic() -> str:
        pass

    @abstractmethod
    def _get_id_from_payload(self, payload: dict) -> str:
        pass

    @abstractmethod
    def _get_db_model_class(self):
        # model_class must inherit from StatefulModel for error handling
        pass

    @property
    def logger(self):
        return self._logger

    async def _get_tenant(self, profile: Profile) -> Tenant:
        async with async_session() as db:
            q = select(Tenant).where(Tenant.id == profile.tenant_id)
            q_result = await db.execute(q)
            db_rec = q_result.scalar_one_or_none()
            return db_rec

    async def _notify(self, profile: Profile, event: Event):
        tenant = await self._get_tenant(profile)
        context["TENANT_WALLET_TOKEN"] = tenant.wallet_token
        payload = event.payload["payload"]
        try:
            await self._perform_task(tenant=tenant, payload=payload)
        except Exception as e:
            await self._handle_perform_task_error(tenant=tenant, payload=payload, exc=e)
            # TODO: send notification via webhook that task errored out

    @abstractmethod
    async def _perform_task(self, tenant: Tenant, payload: dict):
        pass

    async def _handle_perform_task_error(
        self, tenant: Tenant, payload: dict, exc: Exception
    ):
        self.logger.info("> _handle_perform_task_error()")
        item_id = self._get_id_from_payload(payload)
        values = {"status": "Error", "error_status_detail": str(exc)}
        self.logger.warning(values)
        clazz = self._get_db_model_class()
        await clazz.update_by_id(item_id=item_id, values=values)
        self.logger.info("< _handle_perform_task_error()")

    @classmethod
    async def _assign(cls, tenant_id: UUID, wallet_id: UUID, payload):
        """Assign Task.

        Assign a task to be performed.
        Payload will be dependent on the task implementation

        Args:
          tenant_id: Traction ID of tenant making the call
          wallet_id: AcaPy Wallet ID for tenant
          payload: data for the task to run (parsed in _perform_task)
        """
        get_logger(cls).info("> _assign()")
        get_logger(cls).debug(f"tenant_id = {tenant_id}")
        get_logger(cls).debug(f"wallet_id = {wallet_id}")
        get_logger(cls).debug(f"payload = {payload}")
        # create the profile passed to listener/handler
        async with async_session() as db:
            # db is only to satisfy Profile requirements.
            # do NOT use this db anywhere, get a db session when needed in _perform_task
            profile = Profile(wallet_id, tenant_id, db)

        event_topic = cls._event_topic()
        get_logger(cls).debug(f"event_topic = {event_topic}")

        await profile.notify(event_topic, {"topic": "task", "payload": payload})
        get_logger(cls).info("< _assign()")
