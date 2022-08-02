from api.core.profile import Profile
from api.db.models.v1.tenant_job import TenantJobType, TenantJobStatusType, TenantJob
from api.jobs.job_list import Job


class MakeIssuerJob(Job):
    def __init__(self, profile: Profile):
        super().__init__(profile, TenantJobType.issuer)

    async def _do_start(self):
        pass

    async def on_register_public_did_job_active(self, payload: dict):
        self._logger.info("> on_register_public_did_job_active()")
        job = await self._get_job()
        self._logger.info(f"job.status = {job.status}")
        if TenantJobStatusType.approved == job.status:
            await TenantJob.update_by_id(
                job.tenant_job_id, {"status": TenantJobStatusType.processing}
            )
            values = {"status": TenantJobStatusType.active, "data": {"issuer": True}}
            job = await TenantJob.update_by_id(job.tenant_job_id, values)
            await self.fire_event(TenantJobStatusType.active, job.data)

        self._logger.info("< on_register_public_did_job_active()")
