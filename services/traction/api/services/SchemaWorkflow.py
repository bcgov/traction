import json
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from api.api_client_utils import get_api_client
from api.core.profile import Profile
from api.db.errors import DoesNotExist
from api.db.repositories.tenant_schemas import TenantSchemasRepository
from api.db.repositories.tenant_workflows import TenantWorkflowsRepository
from api.db.models.tenant_schema import TenantSchemaUpdate
from api.db.models.tenant_workflow import (
    TenantWorkflowRead,
    TenantWorkflowUpdate,
)
from api.endpoints.models.tenant_workflow import (
    TenantWorkflowStateType,
)
from api.endpoints.models.webhooks import (
    WebhookTopicType,
)

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


class SchemaWorkflow:
    """Workflow to create a schema and/or cred def for a tenant Issuer."""

    @classmethod
    async def find_workflow_id(
        cls, profile: Profile, webhook_message: dict
    ):
        # find related workflow
        schemas_repo = TenantSchemasRepository(db_session=profile.db)
        if webhook_message["topic"] == "endorse_transaction":
            try:
                # look up tenant_schema based on the transaction id
                txn_id = webhook_message["payload"]["transaction_id"]
                tenant_schema = await schemas_repo.get_by_transaction_id(txn_id)
                return tenant_schema.workflow_id
            except DoesNotExist:
                # no related workflow so ignore, for now ...
                return None
        else:
            return None

    def __init__(self, db: AsyncSession, tenant_workflow: TenantWorkflowRead):
        """
        Initialize a new `SchemaWorkflow` instance.
        """
        self._db = db
        self._tenant_workflow = tenant_workflow
        self._schema_repo = TenantSchemasRepository(db_session=db)
        self._workflow_repo = TenantWorkflowsRepository(db_session=db)

    @property
    def db(self) -> AsyncSession:
        """Accessor for db session instance."""
        return self._db

    @property
    def tenant_workflow(self) -> TenantWorkflowRead:
        """Accessor for tenant_workflow instance."""
        return self._tenant_workflow

    @property
    def schema_repo(self) -> TenantSchemasRepository:
        """Accessor for schema_repo instance."""
        return self._schema_repo

    @property
    def workflow_repo(self) -> TenantWorkflowsRepository:
        """Accessor for workflow_repo instance."""
        return self._workflow_repo

    async def run_step(self, webhook_message: dict = None) -> TenantWorkflowRead:
        tenant_schema = await self.schema_repo.get_by_workflow_id(
            self.tenant_workflow.id
        )
        logger.warn(f">>> schema at start of workflow: {tenant_schema}")

        # if workflow is "pending" then we need to start it
        # called direct from the tenant admin api so the tenant is "in context"
        if self.tenant_workflow.workflow_state == TenantWorkflowStateType.pending:
            logger.warn(">>> Initiating workflow ...")
            # update the workflow status as "in_progress"
            update_workflow = TenantWorkflowUpdate(
                id=self.tenant_workflow.id,
                workflow_state=TenantWorkflowStateType.in_progress,
                wallet_bearer_token=self.tenant_workflow.wallet_bearer_token,
            )
            self._tenant_workflow = await self.workflow_repo.update(update_workflow)
            logger.warn(f">>> Started workflow: {self.tenant_workflow}")

            # first step is to initiate creation of the schema or cred def
            logger.warn(f">>> Check for create schema ... {tenant_schema}")
            if tenant_schema.schema_state == TenantWorkflowStateType.pending:
                schema_request = SchemaSendRequest(
                    schema_name=tenant_schema.schema_name,
                    schema_version=tenant_schema.schema_version,
                    attributes=json.loads(tenant_schema.schema_attrs),
                )
                data = {"body": schema_request}
                schema_response = schema_api.schemas_post(**data)
                # we get back either "schema_response.sent" or "schema_response.txn"
                schema_response.txn["transaction_id"]

                # add the endorser connection id to our tenant issuer setup
                update_schema = TenantSchemaUpdate(
                    id=tenant_schema.id,
                    workflow_id=self.tenant_workflow.id,
                    schema_txn_id=schema_response.txn["transaction_id"],
                    schema_state=TenantWorkflowStateType.in_progress,
                    cred_def_state=tenant_schema.cred_def_state,
                )
                tenant_schema = await self.schema_repo.update(update_schema)

            elif tenant_schema.cred_def_state == TenantWorkflowStateType.pending:
                # TODO
                logger.warn(">>> TODO next schema workflow step ...")
                pass

        # if workflow is "in_progress" we need to check what state we are at,
        # ... and initiate the next step (if applicable)
        # called on receipt of webhook, so need to put the proper tenant "in context"
        elif self.tenant_workflow.workflow_state == TenantWorkflowStateType.in_progress:
            logger.warn(
                f">>> run_step() called for in_progress workflow with {webhook_message}"
            )
            webhook_topic = webhook_message["topic"]
            if webhook_topic == WebhookTopicType.endorse_transaction:
                # TODO once we need to handle endorsements
                pass

            else:
                logger.warn(f">>> ignoring topic for now: {webhook_topic}")

        # if workflow is "completed" or "error" then we are done
        else:
            pass

        return self.tenant_workflow
