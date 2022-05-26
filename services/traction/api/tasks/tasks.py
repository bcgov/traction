import logging

from sqlalchemy import select, update
from starlette_context import context

from acapy_client.api.issue_credential_v1_0_api import IssueCredentialV10Api
from acapy_client.model.credential_definition_send_request import (
    CredentialDefinitionSendRequest,
)
from acapy_client.model.v10_credential_free_offer_request import (
    V10CredentialFreeOfferRequest,
)
from api.core.config import settings
from api.core.event_bus import Event
from api.core.profile import Profile
from api.db.models import Tenant
from api.db.models.v1.governance import SchemaTemplate, CredentialTemplate
from api.db.models.v1.issuer import IssuerCredential
from api.db.session import async_session
from api.endpoints.models.v1.errors import NotFoundError
from api.endpoints.models.webhooks import (
    TRACTION_CREATE_SCHEMA_PATTERN,
    TRACTION_CREATE_CRED_DEF_PATTERN,
    TRACTION_OFFER_CREDENTIAL_PATTERN,
)
from acapy_client.api.endorse_transaction_api import EndorseTransactionApi
from acapy_client.api.schema_api import SchemaApi
from acapy_client.api.credential_definition_api import CredentialDefinitionApi
from acapy_client.model.schema_send_request import SchemaSendRequest

from api.api_client_utils import get_api_client
from api.services.v1 import issuer_service

endorse_api = EndorseTransactionApi(api_client=get_api_client())
schema_api = SchemaApi(api_client=get_api_client())
cred_def_api = CredentialDefinitionApi(api_client=get_api_client())
issue_cred_v10_api = IssueCredentialV10Api(api_client=get_api_client())


logger = logging.getLogger(__name__)


def subscribe_task_listeners():
    TaskMaster()


class TaskMaster:
    def __init__(self):
        settings.EVENT_BUS.subscribe(TRACTION_CREATE_SCHEMA_PATTERN, self.create_schema)
        settings.EVENT_BUS.subscribe(
            TRACTION_CREATE_CRED_DEF_PATTERN, self.create_cred_def
        )
        settings.EVENT_BUS.subscribe(
            TRACTION_OFFER_CREDENTIAL_PATTERN, self.offer_credential
        )

    async def get_tenant(self, profile: Profile) -> Tenant:
        async with async_session() as db:
            q = select(Tenant).where(Tenant.id == profile.tenant_id)
            q_result = await db.execute(q)
            db_rec = q_result.scalar_one_or_none()
            return db_rec

    async def create_schema(self, profile: Profile, event: Event):
        tenant = await self.get_tenant(profile)
        context["TENANT_WALLET_TOKEN"] = tenant.wallet_token
        payload = event.payload["payload"]
        schema_definition = payload["schema_definition"]
        schema_template_id = payload["schema_template_id"]
        schema_request = SchemaSendRequest(
            schema_name=schema_definition.schema_name,
            schema_version=schema_definition.schema_version,
            attributes=schema_definition.attributes,
        )
        data = {"body": schema_request}
        resp = schema_api.schemas_post(**data)
        try:
            if resp["txn"]:
                values = {
                    "schema_id": resp["txn"]["meta_data"]["context"]["schema_id"],
                    "transaction_id": resp["txn"]["transaction_id"],
                }
                q = (
                    update(SchemaTemplate)
                    .where(SchemaTemplate.schema_template_id == schema_template_id)
                    .values(values)
                )
                async with async_session() as db:
                    await db.execute(q)
                    await db.commit()
        except AttributeError:
            logger.error()

    async def create_cred_def(self, profile: Profile, event: Event):
        tenant = await self.get_tenant(profile)
        context["TENANT_WALLET_TOKEN"] = tenant.wallet_token
        payload = event.payload["payload"]
        c_t_id = payload["credential_template_id"]
        try:
            async with async_session() as db:
                item = await CredentialTemplate.get_by_id(db, profile.tenant_id, c_t_id)

            cred_def_request = CredentialDefinitionSendRequest(
                schema_id=item.schema_id,
                tag=item.tag,
            )
            if item.revocation_enabled:
                cred_def_request.support_revocation = True
                cred_def_request.revocation_registry_size = (
                    item.revocation_registry_size
                )

            data = {"body": cred_def_request}
            cred_def_response = cred_def_api.credential_definitions_post(**data)

            values = {"transaction_id": cred_def_response.txn["transaction_id"]}
            q = (
                update(CredentialTemplate)
                .where(CredentialTemplate.credential_template_id == c_t_id)
                .values(values)
            )
            async with async_session() as db:
                await db.execute(q)
                await db.commit()

        except NotFoundError:
            logger.error(
                f"No Credential Template for id<{c_t_id}>. Cannot send request to ledger."  # noqa: E501
            )

    async def offer_credential(self, profile: Profile, event: Event):
        tenant = await self.get_tenant(profile)
        context["TENANT_WALLET_TOKEN"] = tenant.wallet_token
        payload = event.payload["payload"]
        issuer_credential_id = payload["issuer_credential_id"]
        try:
            async with async_session() as db:
                item = await IssuerCredential.get_by_id(
                    db, tenant.id, issuer_credential_id
                )
            cred_preview = issuer_service.credential_preview_conversion(item)

            cred_offer = V10CredentialFreeOfferRequest(
                connection_id=str(item.contact.connection_id),
                cred_def_id=item.credential_template.cred_def_id,
                credential_preview=cred_preview,
                comment=item.comment,
                auto_issue=True,
                auto_remove=False,
            )
            data = {"body": cred_offer}
            cred_response = issue_cred_v10_api.issue_credential_send_offer_post(**data)

            values = {
                "credential_exchange_id": cred_response.credential_exchange_id,
                "thread_id": cred_response.thread_id,
            }
            if not item.preview_persisted:
                # remove the preview/attributes...
                values["credential_preview"] = {}

            logger.info(values)
            q = (
                update(IssuerCredential)
                .where(
                    IssuerCredential.issuer_credential_id == item.issuer_credential_id
                )
                .values(values)
            )
            async with async_session() as db:
                await db.execute(q)
                await db.commit()

        except NotFoundError:
            logger.error(
                f"No Issuer Credential found for id<{issuer_credential_id}>. Cannot offer credential."  # noqa: E501
            )
