import logging
import re
from abc import ABC, abstractmethod

from typing import List, TypeVar, Dict


from sqlalchemy import select
from starlette_context import context

from api.core.config import settings
from api.core.event_bus import Event
from api.core.profile import Profile
from api.db.models import Tenant
from api.db.models.v1.tenant_job import TenantJob, TenantJobType, TenantJobStatusType
from api.db.session import async_session

TRACTION_JOB_PREFIX = "traction::JOB"
TRACTION_JOB_LISTENER_PATTERN = re.compile(f"^{TRACTION_JOB_PREFIX}(.*)?$")

JobClassType = TypeVar("JobClassType")


class Job(ABC):
    def __init__(self, profile: Profile, job_type: TenantJobType):
        self._logger = logging.getLogger(type(self).__name__)
        self.profile = profile
        self.job_type = job_type
        self.state_handlers = {
            str(e.value).lower(): self._empty_state_handler for e in TenantJobStatusType
        }

    async def _empty_state_handler(self, payload: dict):
        # this is an empty function assigned to each job status as a default handler
        # inheriting class needs a specific implementation, they can assign a function
        pass

    async def _get_tenant(self) -> Tenant:
        async with async_session() as db:
            q = select(Tenant).where(Tenant.id == self.profile.tenant_id)
            q_result = await db.execute(q)
            db_rec = q_result.scalar_one_or_none()
            return db_rec

    async def _get_job(self) -> TenantJob:
        async with async_session() as db:
            return await TenantJob.get_for_tenant(
                db, self.profile.tenant_id, self.job_type
            )

    async def start(self, dependencies: List[JobClassType] | None = []):
        self._logger.info(f"> start({dependencies})")
        # check dependencies, execute if needed...
        dependencies_active = 0
        for dependency in dependencies:
            j = dependency(self.profile)
            if j.status == TenantJobStatusType.active:
                dependencies_active += 1
            else:
                await j.start()

        if dependencies_active == len(dependencies):
            # all dependencies completed... let's get started
            await self._do_start()

        self._logger.info(f"< start({dependencies})")

    async def fire_event(self, job_event_type: TenantJobStatusType, payload: dict):
        topic = f"{self.job_name()}::{job_event_type}".lower()
        self._logger.info(f"firing event (topic={topic}, payload={payload})")
        await self.profile.notify(
            TRACTION_JOB_PREFIX, {"topic": topic, "payload": payload}
        )

    async def approve(self):
        # most likely called by the innkeeper...
        # just mark as approved, let other process start it
        job = await self._get_job()
        await TenantJob.update_by_id(
            job.tenant_job_id, {"status": TenantJobStatusType.approved}
        )

    async def execute(self, topic: str, payload: dict):
        # called by the job list... tell job to do something to handle event
        self._logger.info(f"> execute({topic}, {payload})")
        tenant = await self._get_tenant()
        self._logger.info(f"tenant = {tenant}")
        context["TENANT_WALLET_TOKEN"] = tenant.wallet_token
        # fetch the current state of the job from db...
        names = topic.split("::")
        job_name = names[0]
        event_name = names[1]
        if job_name == self.job_name():
            # call our event handler...
            on_func = self.state_handlers[event_name]
            self._logger.info(f"on_func = {on_func}")
            await on_func(payload)
        else:
            # try a specific function (to handle event from other job)
            on_func = f"on_{job_name}_{event_name}"
            await self._call_event_func(on_func, payload)

        self._logger.info(f"< execute({payload})")

    async def _call_event_func(self, func_name: str, payload: dict):
        if hasattr(self, func_name) and callable(func := getattr(self, func_name)):
            await func(payload)

    @classmethod
    def job_name(cls):
        return re.sub(r"(?<!^)(?=[A-Z])", "_", cls.__name__).lower()

    async def status(self):
        job = await self._get_job()
        return job.status

    @abstractmethod
    async def _do_start(self):
        pass


class JobList:
    def __init__(self):
        self._logger = logging.getLogger(type(self).__name__)
        settings.EVENT_BUS.subscribe(TRACTION_JOB_LISTENER_PATTERN, self._notify)
        self.subscriptions: Dict[str, List[JobClassType]] = {}

    async def _notify(self, profile: Profile, event: Event):
        self._logger.info(f"> _notify({profile.tenant_id}, {event})")
        topic = event.payload["topic"]
        payload = event.payload["payload"]
        for t, job_clazz_types in self.subscriptions.items():
            if topic == t:
                for job_clazz in job_clazz_types:
                    # create a job using this profile...
                    job = job_clazz(profile)
                    await job.execute(t, payload)
        self._logger.info(f"< _notify({profile.tenant_id}, {event})")

    def subscribe(
        self,
        job_type: JobClassType,
        job_name: str,
        job_status_type: TenantJobStatusType | None = None,
    ):
        self._logger.info(f"> subscribe({job_type}, {job_name}, {job_status_type})")
        events = self._build_events_list(job_status_type)

        for event_name in events:
            key = f"{job_name}::{event_name}".lower()
            if key not in self.subscriptions:
                self.subscriptions[key] = []
            if job_type not in self.subscriptions[key]:
                self.subscriptions[key].append(job_type)
        self._logger.info(
            f"< subscribe({job_type}, {job_name}, {job_status_type}): {self.subscriptions}"  # noqa: E501
        )

    def _build_events_list(self, job_status_type):
        events = []
        if job_status_type is None:
            for jst in TenantJobStatusType:
                events.append(jst.name)
        else:
            events.append(job_status_type)
        return events

    @classmethod
    async def assign(
        cls,
        profile: Profile,
        payload: dict,
        job_type: JobClassType,
        job_event_type: TenantJobStatusType,
    ):

        topic = f"{job_type.job_name}::{job_event_type}".lower()
        await profile.notify(TRACTION_JOB_PREFIX, {"topic": topic, "payload": payload})
