from api.core.config import settings
from api.core.profile import Profile
from api.db.models.v1.tenant_job import TenantJobType, TenantJobStatusType, TenantJob
from api.jobs.job_list import Job
from api.services.connections import receive_invitation


class EndorserConnectionJob(Job):
    def __init__(self, profile: Profile):
        super().__init__(profile, TenantJobType.endorser)

    async def _do_start(self):
        self._logger.info("> _do_start()")
        job = await self._get_job()
        self._logger.info(f"job.status = {job.status}")
        if TenantJobStatusType.approved:
            self._logger.info("approved, so let the work begin...")
            await TenantJob.update_by_id(
                job.tenant_job_id, {"status": TenantJobStatusType.processing}
            )
            # endorser, we need to start the connection
            # let the connection handler call back when completed.
            endorser_alias = settings.ENDORSER_CONNECTION_ALIAS
            endorser_public_did = settings.ACAPY_ENDORSER_PUBLIC_DID
            connection = receive_invitation(
                endorser_alias, their_public_did=endorser_public_did
            )
            self._logger.debug(f"endorser connection = {connection}")

        self._logger.info("< _do_start()")

    async def on_requested(self, payload: dict):
        self._logger.info(f"on_requested({payload})")

    async def on_approved(self, payload: dict):
        self._logger.info(f"on_approved({payload})")

    async def on_processing(self, payload: dict):
        self._logger.info("> on_processing()")
        job = await self._get_job()
        await TenantJob.update_by_id(job.tenant_job_id, {"state": payload["state"]})
        self._logger.info("< on_processing()")

    async def on_denied(self, payload: dict):
        self._logger.info(f"on_denied({payload})")

    async def on_completed(self, payload: dict):
        self._logger.info("> on_completed()")
        job = await self._get_job()
        # no data to store?
        await TenantJob.update_by_id(
            job.tenant_job_id,
            {"status": TenantJobStatusType.active, "state": payload["state"]},
        )
        # let everyone now this job is done!
        await self.fire_event(TenantJobStatusType.active, payload)
        self._logger.info("< on_completed()")

    async def on_error(self, payload: dict):
        self._logger.info(f"on_error({payload})")
