from api.db.models.v1.tenant_job import TenantJobStatusType
from api.jobs.endorser_connection_job import EndorserConnectionJob
from api.jobs.job_list import JobList
from api.jobs.make_issuer_job import MakeIssuerJob
from api.jobs.register_public_did_job import RegisterPublicDidJob


def subscribe_job_list():
    job_list = JobList()
    # make issuer job needs to know when public did job is active
    job_list.subscribe(
        MakeIssuerJob, RegisterPublicDidJob.job_name(), TenantJobStatusType.active
    )
    # register public did needs to know when endorser job is active
    job_list.subscribe(
        RegisterPublicDidJob,
        EndorserConnectionJob.job_name(),
        TenantJobStatusType.active,
    )
    # want the endorser job to listen to all endorser job events
    job_list.subscribe(
        EndorserConnectionJob,
        EndorserConnectionJob.job_name(),
    )
