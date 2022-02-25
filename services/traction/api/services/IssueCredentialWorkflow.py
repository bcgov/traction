import json
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from api.api_client_utils import get_api_client
from api.core.config import settings
from api.core.event_bus import Event
from api.core.profile import Profile
from api.db.errors import DoesNotExist
from api.db.repositories.issue_credentials import IssueCredentialsRepository
from api.db.models.issue_credential import IssueCredentialUpdate, IssueCredentialRead
from api.db.models.tenant_workflow import TenantWorkflowRead
from api.endpoints.models.tenant_workflow import (
    TenantWorkflowStateType,
)
from api.endpoints.models.webhooks import (
    WebhookTopicType,
)
from api.services.base import BaseWorkflow

from acapy_client.api.schema_api import SchemaApi
from acapy_client.api.credential_definition_api import CredentialDefinitionApi


logger = logging.getLogger(__name__)

schema_api = SchemaApi(api_client=get_api_client())
cred_def_api = CredentialDefinitionApi(api_client=get_api_client())


class IssueCredentialWorkflow(BaseWorkflow):
    """Workflow to issue a credential."""

    @classmethod
    async def handle_worklflow_events(cls, profile: Profile, event: Event):
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
        issue_repo = IssueCredentialsRepository(db_session=profile.db)
        if webhook_message["topic"].startswith("issue-credential"):
            try:
                # look up issue_cred based on the cred exchange id
                cred_exch_id = webhook_message["payload"]["credential_exchange_id"]
                issue_cred = await issue_repo.get_by_cred_exch_id(cred_exch_id)
                return issue_cred.workflow_id
            except DoesNotExist:
                # no related workflow so ignore, for now ...
                return None
        else:
            return None

    def __init__(self, db: AsyncSession, tenant_workflow: TenantWorkflowRead):
        """
        Initialize a new `IssueCredentialWorkflow` instance.
        """
        super(IssueCredentialWorkflow, self).__init__(db, tenant_workflow)
        self._issue_repo = IssueCredentialsRepository(db_session=db)

    @property
    def issue_repo(self) -> IssueCredentialsRepository:
        """Accessor for issue_repo instance."""
        return self._issue_repo

    async def run_step(self, webhook_message: dict = None) -> TenantWorkflowRead:
        issue_cred = await self.issue_repo.get_by_workflow_id(
            self.tenant_workflow.id
        )

        # if workflow is "pending" then we need to start it
        # called direct from the tenant admin api so the tenant is "in context"
        if self.tenant_workflow.workflow_state == TenantWorkflowStateType.pending:
            # update the workflow status as "in_progress"
            await self.start_workflow()

            issue_cred = await self.issue_credential(issue_cred)

        # if workflow is "in_progress" we need to check what state we are at,
        # ... and initiate the next step (if applicable)
        # called on receipt of webhook, so need to put the proper tenant "in context"
        elif self.tenant_workflow.workflow_state == TenantWorkflowStateType.in_progress:
            workflow_completed = False
            webhook_topic = webhook_message["topic"]
            if webhook_topic == WebhookTopicType.issue_credential:
                # check for state of "credential_acked"
                webhook_state = webhook_message["payload"]["state"]
                """
                txn_id = webhook_message["payload"]["transaction_id"]
                if webhook_state == "transaction_acked":
                    if txn_id == str(tenant_schema.schema_txn_id):
                        # mark schema completed and kick off cred def
                        tenant_schema = await self.complete_schema(
                            tenant_schema,
                            webhook_message["payload"]["meta_data"]["context"][
                                "schema_id"
                            ],
                        )

                        if (
                            tenant_schema.cred_def_state
                            == TenantWorkflowStateType.pending
                        ):
                            tenant_schema = await self.initiate_cred_def(tenant_schema)
                        else:
                            workflow_completed = True

                    elif txn_id == str(tenant_schema.cred_def_txn_id):
                        # derive the cred_def_id
                        endorser_public_did = settings.ACAPY_ENDORSER_PUBLIC_DID
                        signature_json = webhook_message["payload"][
                            "signature_response"
                        ][0]["signature"][endorser_public_did]
                        tenant_schema = await self.complete_cred_def(
                            tenant_schema, signature_json
                        )
                        workflow_completed = True
                """
                if workflow_completed:
                    # finish off our workflow
                    await self.complete_workflow()

            else:
                logger.warn(f">>> ignoring topic for now: {webhook_topic}")

        # if workflow is "completed" or "error" then we are done
        else:
            pass

        return self.tenant_workflow

    async def issue_credential(
        self, issue_cred: IssueCredentialRead
    ) -> IssueCredentialRead:
        """
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
        )
        tenant_schema = await self.schema_repo.update(update_schema)
        """
        return issue_cred

    async def complete_credential(
        self, issue_cred: IssueCredentialRead
    ) -> IssueCredentialRead:
        """
        update_schema = TenantSchemaUpdate(
            id=tenant_schema.id,
            workflow_id=tenant_schema.workflow_id,
            schema_txn_id=tenant_schema.schema_txn_id,
            schema_id=schema_id,
            schema_state=TenantWorkflowStateType.completed,
            cred_def_state=tenant_schema.cred_def_state,
        )
        tenant_schema = await self.schema_repo.update(update_schema)
        """
        return issue_cred
