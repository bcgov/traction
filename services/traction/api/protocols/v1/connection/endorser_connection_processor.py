import logging
import time
from api.api_client_utils import get_api_client
from api.db.session import async_session
from api.db.repositories.tenant_issuers import (
    TenantIssuersRepository,
    TenantIssuerUpdate,
)

from api.core.profile import Profile
from api.endpoints.models.webhooks import TenantEventTopicType, TRACTION_EVENT_PREFIX
from api.protocols.v1.connection.connection_protocol import DefaultConnectionProtocol

from acapy_client.api.connection_api import ConnectionApi
from acapy_client.api.endorse_transaction_api import EndorseTransactionApi
from api.core.config import settings

from api.endpoints.models.connections import ConnectionRoleType

connection_api = ConnectionApi(api_client=get_api_client())
endorse_api = EndorseTransactionApi(api_client=get_api_client())

logger = logging.getLogger(__name__)


class EndorserConnectionProcessor(DefaultConnectionProtocol):
    def __init__(self):
        # i don't understand the roles, but this one worked, to be discussed
        super().__init__(role=ConnectionRoleType.invitee)

    async def on_completed(self, profile: Profile, payload: dict):
        self.logger.info("> on_completed()")
        topic = TenantEventTopicType.connection
        event_topic = TRACTION_EVENT_PREFIX + topic
        self.logger.debug(f"profile.notify {event_topic}")

        connection_id = payload["connection_id"]

        if payload["alias"] == settings.ENDORSER_CONNECTION_ALIAS:
            from api.tasks.public_did_task import RegisterPublicDIDTask

            self.logger.info(
                f"update meta on endorser connection, connection_id={connection_id}"
            )
            self.update_connection_metadata(connection_id)

            # also update tenant_issuer record with details
            async with async_session() as db:
                # TODO replace when repo pattern is gone
                repo = TenantIssuersRepository(db)
                tenant_issuer = await repo.get_by_tenant_id(profile.tenant_id)
                update_tenant = TenantIssuerUpdate(
                    id=tenant_issuer.id,
                    endorser_connection_id=payload["connection_id"],
                    endorser_connection_state=payload["state"],
                )
                repo.update(update_tenant)
            time.sleep(5)

            RegisterPublicDIDTask.assign(profile.tenant_id, profile.wallet_id, {})
            pass

        await profile.notify(event_topic, {"topic": topic, "payload": payload})

        self.logger.info("< on_completed()")

    def update_connection_metadata(self, connection_id: str):
        logger.debug(f">>> checking for metadata on connection: {connection_id}")
        conn_meta_data = connection_api.connections_conn_id_metadata_get(connection_id)
        add_meta_data = True
        if "transaction-jobs" in conn_meta_data.results:
            if "transaction_my_job" in conn_meta_data.results["transaction-jobs"]:
                add_meta_data = False

        if add_meta_data:
            logger.debug(f">>> add metadata to endorser connection: {connection_id}")
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
