import requests

import acapy_client
from acapy_client.model.did_create import DIDCreate
from acapy_client.model.did_result import DIDResult
from acapy_client.model.register_ledger_nym_response import RegisterLedgerNymResponse
from api.core.config import settings
from api.core.profile import Profile
from api.db.models import Tenant
from api.db.models.v1.tenant_job import TenantJobType, TenantJobStatusType, TenantJob
from api.jobs.job_list import Job
from api.services.v1.acapy_service import wallet_api, ledger_api


class RegisterPublicDidJob(Job):
    def __init__(self, profile: Profile):
        super().__init__(profile, TenantJobType.public_did)

    async def _do_start(self):
        pass

    async def on_requested(self, payload: dict):
        pass

    async def on_approved(self, payload: dict):
        pass

    async def on_processing(self, payload: dict):
        pass

    async def on_denied(self, payload: dict):
        pass

    async def on_completed(self, payload: dict):
        pass

    async def on_error(self, payload: dict):
        pass

    async def on_endorser_connection_job_active(self, payload: dict):
        self._logger.info("> on_endorser_connection_job_active()")
        job = await self._get_job()
        tenant = await self._get_tenant()
        self._logger.info(f"job.status = {job.status}")
        if TenantJobStatusType.approved == job.status:
            # start the processing...
            await TenantJob.update_by_id(
                job.tenant_job_id, {"status": TenantJobStatusType.processing}
            )
            await self.initiate_public_did(job, tenant)

            # make this active and let everyone know...
            job = await TenantJob.update_by_id(
                job.tenant_job_id, {"status": TenantJobStatusType.active}
            )
            await self.fire_event(TenantJobStatusType.active, job.data)

        self._logger.info("< on_endorser_connection_job_active()")

    async def initiate_public_did(self, job: TenantJob, tenant: Tenant) -> None:
        self._logger.info("> initiate_public_did())")
        await TenantJob.update_by_id(
            job.tenant_job_id, {"status": TenantJobStatusType.processing}
        )

        # onto the next phase!  create our DID and make it public
        did_result = await self.create_local_did()

        # post to the ledger (this will be an endorser operation)
        # (just ignore the response for now)
        try:
            await self.initiate_public_did_workflow(tenant, did_result)
        except acapy_client.ApiException as e:
            self._logger.error(f"initiate_public_did_workflow exception: {e.reason}")
            # TODO this is a hack (for now) - aca-py 0.7.3 doesn't
            # support the endorser protocol for this transaction, it
            # will be in the next release (0.7.4 or whatever)
            did_result = await self.create_public_did(tenant, did_result)

        # now let's complete the flow
        values = {
            "status": TenantJobStatusType.completed,
            "data": {"did": did_result.result.did},
        }
        self._logger.info(f"update job values = {values}")
        await TenantJob.update_by_id(job.tenant_job_id, values)
        self._logger.info("< initiate_public_did()")
        return

    async def create_local_did(self) -> DIDResult:
        self._logger.info("> create_local_did()")
        data = {"body": DIDCreate()}
        result = wallet_api.wallet_did_create_post(**data)
        self._logger.info(f"< create_local_did({result})")
        return result

    async def initiate_public_did_workflow(
        self, tenant: Tenant, did_result: DIDResult
    ) -> RegisterLedgerNymResponse:
        self._logger.info(f"> initiate_public_did_workflow({did_result})")
        data = {"alias": str(tenant.id)}
        result = ledger_api.ledger_register_nym_post(
            did_result.result.did,
            did_result.result.verkey,
            **data,
        )
        self._logger.info(f"< initiate_public_did_workflow({did_result}) = {result}")
        return result

    async def create_public_did(
        self, tenant: Tenant, did_result: DIDResult
    ) -> DIDResult:
        self._logger.info(f"> create_public_did({did_result})")
        genesis_url = settings.ACAPY_GENESIS_URL
        did_registration_url = genesis_url.replace("genesis", "register")
        data = {
            "did": did_result.result.did,
            "verkey": did_result.result.verkey,
            "alias": str(tenant.id),
        }
        requests.post(did_registration_url, json=data)
        # now make it public
        result = wallet_api.wallet_did_public_post(did_result.result.did)
        self._logger.info(f"< create_public_did({did_result}) = {result}")
        return result
