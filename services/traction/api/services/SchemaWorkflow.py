import json
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from api.api_client_utils import get_api_client
from api.core.config import settings
from api.core.event_bus import Event
from api.core.profile import Profile
from api.db.errors import DoesNotExist
from api.db.repositories.tenant_schemas import TenantSchemasRepository
from api.db.models.tenant_schema import TenantSchemaUpdate, TenantSchemaRead
from api.db.models.tenant_workflow import TenantWorkflowRead
from api.endpoints.models.tenant_workflow import (
    TenantWorkflowStateType,
)
from api.endpoints.models.webhooks import (
    WebhookTopicType,
)
from api.services.base import BaseWorkflow

from acapy_client.api.endorse_transaction_api import EndorseTransactionApi
from acapy_client.api.schema_api import SchemaApi
from acapy_client.api.credential_definition_api import CredentialDefinitionApi
from acapy_client.model.schema_send_request import SchemaSendRequest
from acapy_client.model.credential_definition_send_request import (
    CredentialDefinitionSendRequest,
)


logger = logging.getLogger(__name__)

endorse_api = EndorseTransactionApi(api_client=get_api_client())
schema_api = SchemaApi(api_client=get_api_client())
cred_def_api = CredentialDefinitionApi(api_client=get_api_client())


class SchemaWorkflow(BaseWorkflow):
    """Workflow to create a schema and/or cred def for a tenant Issuer."""

    @classmethod
    async def handle_workflow_events(cls, profile: Profile, event: Event):
        # find related workflow
        try:
            workflow_id = await cls.find_workflow_id(profile, event.payload)
            if workflow_id:
                await cls.next_workflow_step(
                    profile.db,
                    workflow_id=workflow_id,
                    webhook_message=event.payload,
                )
            else:
                return
        except DoesNotExist:
            # no related workflow so ignore, for now ...
            return

    @classmethod
    async def find_workflow_id(cls, profile: Profile, webhook_message: dict):
        # find related workflow
        schemas_repo = TenantSchemasRepository(db_session=profile.db)
        if webhook_message["topic"] == "endorse_transaction":
            try:
                # look up tenant_schema based on the transaction id
                txn_id = webhook_message["payload"]["transaction_id"]
                tenant_schema = await schemas_repo.get_by_transaction_id(txn_id)
                return tenant_schema.workflow_id
            except DoesNotExist:
                pass
            # nothing by txn_id, check based on cred_def_id
            webhook_state = webhook_message["payload"]["state"]
            if not webhook_state == "transaction_acked":
                return None
            try:
                cred_def_id = webhook_message["payload"]["meta_data"]["context"][
                    "cred_def_id"
                ]
                tenant_schema = await schemas_repo.get_by_cred_def_id(cred_def_id)
                return tenant_schema.workflow_id
            except (KeyError, DoesNotExist):
                # no related workflow so ignore, for now ...
                return None
        else:
            return None

    def __init__(self, db: AsyncSession, tenant_workflow: TenantWorkflowRead):
        """
        Initialize a new `SchemaWorkflow` instance.
        """
        super(SchemaWorkflow, self).__init__(db, tenant_workflow)
        self._schema_repo = TenantSchemasRepository(db_session=db)

    @property
    def schema_repo(self) -> TenantSchemasRepository:
        """Accessor for schema_repo instance."""
        return self._schema_repo

    async def run_step(self, webhook_message: dict = None) -> TenantWorkflowRead:
        tenant_schema = await self.schema_repo.get_by_workflow_id(
            self.tenant_workflow.id
        )

        # if workflow is "pending" then we need to start it
        # called direct from the tenant admin api so the tenant is "in context"
        if self.tenant_workflow.workflow_state == TenantWorkflowStateType.pending:
            # update the workflow status as "in_progress"
            await self.start_workflow()

            # first step is to initiate creation of the schema or cred def
            if tenant_schema.schema_state == TenantWorkflowStateType.pending:
                tenant_schema = await self.initiate_schema(tenant_schema)

            elif tenant_schema.cred_def_state == TenantWorkflowStateType.pending:
                tenant_schema = await self.initiate_cred_def(tenant_schema)

        # if workflow is "in_progress" we need to check what state we are at,
        # ... and initiate the next step (if applicable)
        # called on receipt of webhook, so need to put the proper tenant "in context"
        elif self.tenant_workflow.workflow_state == TenantWorkflowStateType.in_progress:
            workflow_completed = False
            webhook_topic = webhook_message["topic"]
            if webhook_topic == WebhookTopicType.endorse_transaction:
                # check for transaction state of "transaction_acked"
                webhook_state = webhook_message["payload"]["state"]
                if webhook_state == "transaction_acked":
                    txn_id = webhook_message["payload"]["transaction_id"]
                    endorser_public_did = settings.ACAPY_ENDORSER_PUBLIC_DID
                    signature_json = webhook_message["payload"]["signature_response"][
                        0
                    ]["signature"][endorser_public_did]
                    signature = json.loads(signature_json)
                    if txn_id == str(tenant_schema.schema_txn_id):
                        (workflow_completed, tenant_schema) = await self.process_schema(
                            tenant_schema, webhook_message
                        )

                    elif txn_id == str(tenant_schema.cred_def_txn_id):
                        (
                            workflow_completed,
                            tenant_schema,
                        ) = await self.process_cred_def(tenant_schema, signature)

                    elif signature["operation"]["type"] == "114" and webhook_message[
                        "payload"
                    ]["meta_data"]["context"]["cred_def_id"] == str(
                        tenant_schema.cred_def_id
                    ):
                        (
                            workflow_completed,
                            tenant_schema,
                        ) = await self.process_revoc(tenant_schema, webhook_message)

                    if workflow_completed:
                        # finish off our workflow
                        await self.complete_workflow()
                        await self.workflow_notifier.schema_workflow_completed(
                            tenant_schema
                        )

            else:
                logger.warn(f">>> ignoring topic for now: {webhook_topic}")

        # if workflow is "completed" or "error" then we are done
        else:
            pass

        return self.tenant_workflow

    async def initiate_schema(
        self, tenant_schema: TenantSchemaRead
    ) -> TenantSchemaRead:
        schema_request = SchemaSendRequest(
            schema_name=tenant_schema.schema_name,
            schema_version=tenant_schema.schema_version,
            attributes=json.loads(tenant_schema.schema_attrs),
        )
        data = {"body": schema_request}
        schema_response = schema_api.schemas_post(**data)
        # we get back either "schema_response.sent" or "schema_response.txn"

        # add the transaction id to our tenant schema setup
        update_schema = TenantSchemaUpdate(
            id=tenant_schema.id,
            workflow_id=self.tenant_workflow.id,
            schema_id=tenant_schema.schema_id,
            schema_txn_id=schema_response.txn["transaction_id"],
            schema_state=TenantWorkflowStateType.in_progress,
            cred_def_state=tenant_schema.cred_def_state,
            revoc_reg_state=tenant_schema.revoc_reg_state,
        )
        tenant_schema = await self.schema_repo.update(update_schema)
        return tenant_schema

    async def process_schema(
        self, tenant_schema: TenantSchemaRead, webhook_message: dict
    ) -> (bool, TenantSchemaRead):
        workflow_completed = False
        if not tenant_schema.schema_state == TenantWorkflowStateType.completed:
            # mark schema completed and kick off cred def
            tenant_schema = await self.complete_schema(
                tenant_schema,
                webhook_message["payload"]["meta_data"]["context"]["schema_id"],
            )

            if tenant_schema.cred_def_state == TenantWorkflowStateType.pending:
                tenant_schema = await self.initiate_cred_def(tenant_schema)
            else:
                workflow_completed = True
        return workflow_completed, tenant_schema

    async def complete_schema(
        self, tenant_schema: TenantSchemaRead, schema_id: str
    ) -> TenantSchemaRead:
        update_schema = TenantSchemaUpdate(
            id=tenant_schema.id,
            workflow_id=tenant_schema.workflow_id,
            schema_txn_id=tenant_schema.schema_txn_id,
            schema_id=schema_id,
            schema_state=TenantWorkflowStateType.completed,
            cred_def_state=tenant_schema.cred_def_state,
            revoc_reg_state=tenant_schema.revoc_reg_state,
        )
        tenant_schema = await self.schema_repo.update(update_schema)
        return tenant_schema

    async def initiate_cred_def(
        self, tenant_schema: TenantSchemaRead
    ) -> TenantSchemaRead:
        cred_def_request = CredentialDefinitionSendRequest(
            schema_id=tenant_schema.schema_id,
            tag=tenant_schema.cred_def_tag,
        )
        if tenant_schema.cred_revocation:
            cred_def_request.support_revocation = tenant_schema.cred_revocation
            cred_def_request.revocation_registry_size = (
                tenant_schema.cred_revoc_reg_size
            )

        data = {"body": cred_def_request}
        logger.info(f"cred def request = {data}")
        cred_def_response = cred_def_api.credential_definitions_post(**data)
        # we get back either "cred_def_response.sent" or "cred_def_response.txn"

        # add the transaction id to our tenant schema setup
        update_schema = TenantSchemaUpdate(
            id=tenant_schema.id,
            workflow_id=self.tenant_workflow.id,
            schema_txn_id=tenant_schema.schema_txn_id,
            schema_id=tenant_schema.schema_id,
            schema_state=tenant_schema.schema_state,
            cred_def_txn_id=cred_def_response.txn["transaction_id"],
            cred_def_state=TenantWorkflowStateType.in_progress,
            revoc_reg_state=tenant_schema.revoc_reg_state,
        )
        tenant_schema = await self.schema_repo.update(update_schema)
        return tenant_schema

    async def process_cred_def(
        self, tenant_schema: TenantSchemaRead, signature: dict
    ) -> (bool, TenantSchemaRead):
        workflow_completed = False
        if not tenant_schema.cred_def_state == TenantWorkflowStateType.completed:
            # derive the cred_def_id
            tenant_schema = await self.complete_cred_def(tenant_schema, signature)

            if tenant_schema.revoc_reg_state == TenantWorkflowStateType.pending:
                # nothing to do here, the revocation stuff is kicked off automagically
                pass
            else:
                workflow_completed = True

        return workflow_completed, tenant_schema

    async def complete_cred_def(
        self, tenant_schema: TenantSchemaRead, signature: dict
    ) -> TenantSchemaRead:
        public_did = signature["identifier"]
        sig_type = signature["operation"]["signature_type"]
        schema_ref = signature["operation"]["ref"]
        tag = signature["operation"]["tag"]
        cred_def_id = f"{public_did}:3:{sig_type}:{schema_ref}:{tag}"

        # mark cred def completed
        update_schema = TenantSchemaUpdate(
            id=tenant_schema.id,
            workflow_id=tenant_schema.workflow_id,
            schema_txn_id=tenant_schema.schema_txn_id,
            schema_id=tenant_schema.schema_id,
            schema_state=TenantWorkflowStateType.completed,
            cred_def_txn_id=tenant_schema.cred_def_txn_id,
            cred_def_id=cred_def_id,
            cred_def_state=TenantWorkflowStateType.completed,
            revoc_reg_state=tenant_schema.revoc_reg_state,
        )
        tenant_schema = await self.schema_repo.update(update_schema)
        return tenant_schema

    async def process_revoc(
        self, tenant_schema: TenantSchemaRead, webhook_message: dict
    ) -> (bool, TenantSchemaRead):
        # mark revoc completed
        update_schema = TenantSchemaUpdate(
            id=tenant_schema.id,
            workflow_id=tenant_schema.workflow_id,
            schema_txn_id=tenant_schema.schema_txn_id,
            schema_id=tenant_schema.schema_id,
            schema_state=TenantWorkflowStateType.completed,
            cred_def_txn_id=tenant_schema.cred_def_txn_id,
            cred_def_id=tenant_schema.cred_def_id,
            cred_def_state=tenant_schema.cred_def_state,
            revoc_reg_state=TenantWorkflowStateType.completed,
        )
        tenant_schema = await self.schema_repo.update(update_schema)
        return (True, tenant_schema)
