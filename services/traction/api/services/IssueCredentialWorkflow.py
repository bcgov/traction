import json
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from api.api_client_utils import get_api_client
from api.core.event_bus import Event
from api.core.profile import Profile
from api.db.errors import DoesNotExist
from api.db.repositories.issue_credentials import IssueCredentialsRepository
from api.db.models.issue_credential import (
    IssueCredentialUpdate,
    IssueCredentialRead,
    IssueCredentialCreate,
)
from api.db.models.tenant_workflow import TenantWorkflowRead

from api.endpoints.dependencies.tenant_security import get_from_context
from api.endpoints.models.tenant_workflow import (
    TenantWorkflowStateType,
)
from api.services.tenant_workflow_notifier import TenantWorkflowNotifier
from api.endpoints.models.credentials import (
    IssueCredentialProtocolType,
    CredentialType,
    CredentialStateType,
    CredentialRoleType,
)
from api.endpoints.models.webhooks import (
    WebhookTopicType,
)
from api.services.base import BaseWorkflow

from acapy_client.api.issue_credential_v1_0_api import IssueCredentialV10Api
from acapy_client.model.cred_attr_spec import CredAttrSpec
from acapy_client.model.credential_preview import CredentialPreview
from acapy_client.model.v10_credential_free_offer_request import (
    V10CredentialFreeOfferRequest,
)
from acapy_client.model.v10_credential_problem_report_request import (
    V10CredentialProblemReportRequest,
)


logger = logging.getLogger(__name__)

issue_cred_v10_api = IssueCredentialV10Api(api_client=get_api_client())


class IssueCredentialWorkflow(BaseWorkflow):
    """Workflow to issue a credential."""

    @classmethod
    async def handle_workflow_events(cls, profile: Profile, event: Event):
        # find related workflow
        logger.warn(f">>> handling event: {event}")
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
        if webhook_message["topic"] == WebhookTopicType.issue_credential:
            try:
                # look up issue_cred based on the cred exchange id
                wallet_id = get_from_context("TENANT_WALLET_ID")
                cred_exch_id = webhook_message["payload"]["credential_exchange_id"]
                issue_cred = await issue_repo.get_by_cred_exch_id(
                    wallet_id, cred_exch_id
                )
                logger.warn(f">>> found corresponding cred issue: {issue_cred}")
                return issue_cred.workflow_id
            except DoesNotExist:
                # no related workflow, check if we (holder) are receiving an offer
                cred_state = webhook_message["payload"]["state"]
                logger.warn(f">>> check for cred issue event for: {cred_state}")
                if cred_state == CredentialStateType.offer_received:
                    wallet_id = get_from_context("TENANT_WALLET_ID")
                    tenant_id = get_from_context("TENANT_ID")
                    payload = webhook_message["payload"]
                    connection_id = payload["connection_id"]
                    cred_def_id = payload["credential_definition_id"]
                    cred_exch_id = payload["credential_exchange_id"]
                    issue_cred = IssueCredentialCreate(
                        tenant_id=tenant_id,
                        wallet_id=wallet_id,
                        connection_id=connection_id,
                        cred_type=CredentialType.anoncreds,
                        cred_protocol=IssueCredentialProtocolType.v10,
                        cred_def_id=cred_def_id,
                        credential=json.dumps(payload["credential_proposal_dict"]),
                        issue_role=CredentialRoleType.holder,
                        issue_state=cred_state,
                        cred_exch_id=cred_exch_id,
                    )
                    issue_cred = await issue_repo.create(issue_cred)
                    logger.warn(f">>> created new cred issue: {issue_cred}")

                    # if new, and offer_received, send webhook to tenant
                    logger.info(f">>> sending webhook with cred offer: {issue_cred}")
                    await TenantWorkflowNotifier(profile.db).issuer_workflow_cred_offer(
                        issue_cred
                    )
                    # return None - we want the tenant to accept the credential offer
                    return None

                return None

        elif webhook_message["topic"] == WebhookTopicType.revocation_notification:
            # update credential status to revoked
            logger.warn(f">>> got a revocation notification: {webhook_message}")
            wallet_id = get_from_context("TENANT_WALLET_ID")
            comment = webhook_message["payload"].get("comment")
            thread_id = webhook_message["payload"].get("thread_id")
            # should be "indy::<rev_reg_id>::<cred_rev_id>"
            thread_id_parts = thread_id.split("::")
            rev_reg_id = thread_id_parts[1]
            cred_rev_id = thread_id_parts[2]
            issue_cred = await issue_repo.get_by_cred_rev_reg_id(
                wallet_id, rev_reg_id, cred_rev_id
            )
            if issue_cred:
                update_issue = IssueCredentialUpdate(
                    id=issue_cred.id,
                    workflow_id=issue_cred.workflow_id,
                    issue_state=CredentialStateType.credential_revoked,
                    cred_exch_id=issue_cred.cred_exch_id,
                )
                issue_cred = await issue_repo.update(update_issue)

                logger.info(f">>> sending webhook with cred revoc: {issue_cred}")
                await TenantWorkflowNotifier(profile.db).issuer_workflow_cred_revoc(
                    issue_cred, comment
                )
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
        wallet_id = get_from_context("TENANT_WALLET_ID")
        issue_cred = await self.issue_repo.get_by_workflow_id(
            wallet_id, self.tenant_workflow.id
        )

        # if workflow is "pending" then we need to start it
        # called direct from the tenant admin api so the tenant is "in context"
        if self.tenant_workflow.workflow_state == TenantWorkflowStateType.pending:
            # update the workflow status as "in_progress"
            await self.start_workflow()

            if issue_cred.issue_role == CredentialRoleType.issuer:
                issue_cred = await self.issuer_issue_credential(issue_cred)

            elif issue_cred.issue_role == CredentialRoleType.holder:
                issue_cred = await self.holder_request_credential(issue_cred)

            else:
                # ignore for now
                pass

        # if workflow is "in_progress" we need to check what state we are at,
        # ... and initiate the next step (if applicable)
        # called on receipt of webhook, so need to put the proper tenant "in context"
        elif self.tenant_workflow.workflow_state == TenantWorkflowStateType.in_progress:
            webhook_topic = webhook_message["topic"]
            logger.debug(f">>> checking for webhook_topic: {webhook_topic}")
            if webhook_topic == WebhookTopicType.issue_credential:
                if webhook_message["payload"].get("state"):
                    # check for state of "credential_acked"
                    webhook_state = webhook_message["payload"]["state"]
                    logger.debug(f">>> checking for webhook_state: {webhook_state}")
                    # update our status
                    issue_cred = await self.update_credential_state(
                        issue_cred, webhook_state
                    )
                    if (
                        webhook_state == CredentialStateType.done
                        or webhook_state == CredentialStateType.credential_acked
                    ):
                        issue_cred = await self.complete_credential(
                            issue_cred, webhook_message
                        )

                        # finish off our workflow
                        await self.complete_workflow()

                elif webhook_message["payload"].get("error_msg"):
                    # we got an error so log it and cancel the workflow
                    error_msg = webhook_message["payload"]["error_msg"]
                    logger.debug(f">>> cancelling workflow with error_msg: {error_msg}")
                    await self.run_cancel_step(webhook_message, error_msg)
            else:
                logger.warn(f">>> ignoring topic for now: {webhook_topic}")

        # if workflow is "completed" or "error" then we are done
        else:
            pass

        return self.tenant_workflow

    async def run_cancel_step(
        self, webhook_message: dict = None, error_msg: str = None
    ) -> TenantWorkflowRead:
        # send a problem report with the given error
        wallet_id = get_from_context("TENANT_WALLET_ID")
        issue_cred = await self.issue_repo.get_by_workflow_id(
            wallet_id, self.tenant_workflow.id
        )
        await self.complete_with_problem_report(issue_cred, webhook_message, error_msg)

        # then cancel te workflow
        await self.complete_workflow_error(error_msg)

        return self.tenant_workflow

    async def issuer_issue_credential(
        self, issue_cred: IssueCredentialRead
    ) -> IssueCredentialRead:
        cred_attrs = []
        attrs = json.loads(issue_cred.credential)
        for attr in attrs["attributes"]:
            cred_attr = CredAttrSpec(
                name=attr["name"],
                value=attr["value"],
            )
            cred_attrs.append(cred_attr)
        cred_preview = CredentialPreview(attributes=cred_attrs)
        cred_offer = V10CredentialFreeOfferRequest(
            connection_id=str(issue_cred.connection_id),
            cred_def_id=issue_cred.cred_def_id,
            credential_preview=cred_preview,
            comment="TBD comment goes here",
            auto_issue=True,
            auto_remove=False,
        )
        data = {"body": cred_offer}
        cred_response = issue_cred_v10_api.issue_credential_send_offer_post(**data)

        # add the transaction id to our tenant schema setup
        update_issue = IssueCredentialUpdate(
            id=issue_cred.id,
            workflow_id=self.tenant_workflow.id,
            issue_state=cred_response.state,
            cred_exch_id=cred_response.credential_exchange_id,
        )
        issue_cred = await self.issue_repo.update(update_issue)
        return issue_cred

    async def holder_request_credential(
        self, issue_cred: IssueCredentialRead
    ) -> IssueCredentialRead:
        cred_response = (
            issue_cred_v10_api.issue_credential_records_cred_ex_id_send_request_post(
                str(issue_cred.cred_exch_id)
            )
        )

        # add the transaction id to our tenant schema setup
        update_issue = IssueCredentialUpdate(
            id=issue_cred.id,
            workflow_id=self.tenant_workflow.id,
            issue_state=cred_response.state,
            cred_exch_id=cred_response.credential_exchange_id,
        )
        issue_cred = await self.issue_repo.update(update_issue)
        return issue_cred

    async def update_credential_state(
        self, issue_cred: IssueCredentialRead, state: str
    ) -> IssueCredentialRead:
        logger.debug(f">>> updating state to {state}")
        update_issue = IssueCredentialUpdate(
            id=issue_cred.id,
            workflow_id=self.tenant_workflow.id,
            issue_state=state,
            cred_exch_id=issue_cred.cred_exch_id,
        )
        issue_cred = await self.issue_repo.update(update_issue)
        return issue_cred

    async def complete_credential(
        self, issue_cred: IssueCredentialRead, webhook_message: dict
    ) -> IssueCredentialRead:
        update_issue = IssueCredentialUpdate(
            id=issue_cred.id,
            workflow_id=self.tenant_workflow.id,
            issue_state=issue_cred.issue_state,
            cred_exch_id=issue_cred.cred_exch_id,
        )
        # capture the revocation info's from the webhook
        if webhook_message["payload"].get("revoc_reg_id"):
            update_issue.rev_reg_id = webhook_message["payload"].get("revoc_reg_id")
            update_issue.cred_rev_id = webhook_message["payload"].get("revocation_id")
        issue_cred = await self.issue_repo.update(update_issue)
        return issue_cred

    async def complete_with_problem_report(
        self, issue_cred: IssueCredentialRead, webhook_message: dict, error_msg: str
    ) -> IssueCredentialRead:
        problem_report = V10CredentialProblemReportRequest(
            description=error_msg,
        )
        data = {"body": problem_report}
        issue_cred_v10_api.issue_credential_records_cred_ex_id_problem_report_post(
            str(issue_cred.cred_exch_id),
            **data,
        )
        return issue_cred
