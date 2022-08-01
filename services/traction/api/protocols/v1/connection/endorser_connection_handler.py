import time

from sqlalchemy import select
from starlette_context import context

from api.core.config import settings
from api.core.profile import Profile
from api.db.models import Tenant
from api.db.models.v1.tenant_job import TenantJobStatusType
from api.db.session import async_session
from api.endpoints.models.connections import ConnectionRoleType

from api.jobs.endorser_connection_job import EndorserConnectionJob
from api.protocols.v1.connection.connection_protocol import DefaultConnectionProtocol
from api.services.v1.acapy_service import connection_api, endorse_api


approved_flows = [
    TenantJobStatusType.approved,
    TenantJobStatusType.processing,
]


class EndorserConnectionHandler(DefaultConnectionProtocol):
    def __init__(self):
        super().__init__(role=ConnectionRoleType.invitee)

    async def get_tenant(self, profile: Profile) -> Tenant:
        async with async_session() as db:
            q = select(Tenant).where(Tenant.id == profile.tenant_id)
            q_result = await db.execute(q)
            db_rec = q_result.scalar_one_or_none()
            return db_rec

    async def approve_for_processing(self, profile: Profile, payload: dict) -> bool:
        self.logger.info("> approve_for_processing()")
        self.logger.debug(f"payload = {payload}")
        # approve if this is endorser and we have a flow to process...
        their_public_did = (
            None if "their_public_did" not in payload else payload["their_public_did"]
        )
        self.logger.debug(f"their_public_did = {their_public_did}")
        endorser_public_did = settings.ACAPY_ENDORSER_PUBLIC_DID
        self.logger.debug(f"endorser_public_did = {endorser_public_did}")
        endorser_connection = endorser_public_did == their_public_did
        job = EndorserConnectionJob(profile)
        job_status = await job.status()
        job_approved = job_status in approved_flows
        self.logger.info(f"endorser_connection = {endorser_connection}")
        self.logger.info(f"job_approved = {job_approved}")
        self.logger.info(f"job.status = {job_status}")
        approved = endorser_connection and job_approved
        self.logger.info(f"< approve_for_processing({approved})")
        return approved

    async def before_any(self, profile: Profile, payload: dict):
        self.logger.info("> before_any()")
        job = EndorserConnectionJob(profile)
        await job.fire_event(TenantJobStatusType.processing, payload)
        self.logger.info("< before_any()")

    async def on_completed(self, profile: Profile, payload: dict):
        self.logger.info("> on_completed()")
        # now this is where we do the public did work...
        tenant = await self.get_tenant(profile)
        context["TENANT_WALLET_TOKEN"] = tenant.wallet_token
        self.update_connection_metadata(payload["connection_id"])

        job = EndorserConnectionJob(profile)
        await job.fire_event(TenantJobStatusType.completed, payload)
        self.logger.info("< before_any()")

    def update_connection_metadata(self, connection_id: str):
        self.logger.debug(f">>> checking for metadata on connection: {connection_id}")
        conn_meta_data = connection_api.connections_conn_id_metadata_get(connection_id)
        add_meta_data = True
        if "transaction-jobs" in conn_meta_data.results:
            if "transaction_my_job" in conn_meta_data.results["transaction-jobs"]:
                add_meta_data = False

        if add_meta_data:
            self.logger.debug(
                f">>> add metadata to endorser connection: {connection_id}"
            )
            # TODO - pause here to prevent race condition with endorser
            # (error if both update endorser role at the same time)
            time.sleep(1)

            # attach some meta-data to the connection
            # TODO verify response from each call ...
            data = {"transaction_my_job": "TRANSACTION_AUTHOR"}
            endorse_api.transactions_conn_id_set_endorser_role_post(
                connection_id, **data
            )
            endorser_alias = settings.ENDORSER_CONNECTION_ALIAS
            endorser_public_did = settings.ACAPY_ENDORSER_PUBLIC_DID
            data = {"endorser_name": endorser_alias}
            endorse_api.transactions_conn_id_set_endorser_info_post(
                connection_id, endorser_public_did, **data
            )
