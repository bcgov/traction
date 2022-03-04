import json
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from api.api_client_utils import get_api_client
from api.core.event_bus import Event
from api.core.profile import Profile
from api.db.errors import DoesNotExist
from api.db.repositories.present_credentials import PresentCredentialsRepository
from api.db.models.present_credential import (
    PresentCredentialUpdate,
    PresentCredentialRead,
    PresentCredentialCreate,
)
from api.db.models.tenant_workflow import TenantWorkflowRead

from api.endpoints.dependencies.tenant_security import get_from_context
from api.endpoints.models.tenant_workflow import (
    TenantWorkflowStateType,
)
from api.endpoints.models.credentials import (
    PresentCredentialProtocolType,
    PresentationStateType,
    PresentationRoleType,
)
from api.endpoints.models.webhooks import (
    WebhookTopicType,
)
from api.services.base import BaseWorkflow

from acapy_client.api.present_proof_v1_0_api import PresentProofV10Api
from acapy_client.model.v10_presentation_send_request_request import (
    V10PresentationSendRequestRequest,
)
from acapy_client.model.indy_proof_request import IndyProofRequest

# from acapy_client.model.indy_proof_req_attr_spec import IndyProofReqAttrSpec
# from acapy_client.model.indy_proof_req_pred_spec import IndyProofReqPredSpec


logger = logging.getLogger(__name__)

pres_cred_v10_api = PresentProofV10Api(api_client=get_api_client())


class PresentCredentialWorkflow(BaseWorkflow):
    """Workflow to present and verify a credential."""

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
        present_repo = PresentCredentialsRepository(db_session=profile.db)
        if webhook_message["topic"] == WebhookTopicType.present_proof:
            try:
                # look up present_cred based on the pres exchange id
                pres_exch_id = webhook_message["payload"]["presentation_exchange_id"]
                present_cred = await present_repo.get_by_pres_exch_id(pres_exch_id)
                logger.warn(f">>> found corresponding cred pres: {present_cred}")
                return present_cred.workflow_id
            except DoesNotExist:
                # no related workflow, check if we (holder) are receiving a request
                pres_state = webhook_message["payload"]["state"]
                logger.warn(f">>> check for cred present event for: {pres_state}")
                if pres_state == PresentationStateType.request_received:
                    wallet_id = get_from_context("TENANT_WALLET_ID")
                    tenant_id = get_from_context("TENANT_ID")
                    payload = webhook_message["payload"]
                    connection_id = payload["connection_id"]
                    pres_exch_id = payload["presentation_exchange_id"]
                    present_cred = PresentCredentialCreate(
                        tenant_id=tenant_id,
                        wallet_id=wallet_id,
                        connection_id=connection_id,
                        cred_protocol=PresentCredentialProtocolType.v10,
                        present_request=json.dumps(payload["presentation_request"]),
                        present_role=PresentationRoleType.holder,
                        present_state=pres_state,
                        pres_exch_id=pres_exch_id,
                    )
                    present_cred = await present_repo.create(present_cred)
                    logger.warn(f">>> created new present request: {present_cred}")

                    # return None - we want the tenant to respond to the request
                    return None

                return None
        else:
            return None

    def __init__(self, db: AsyncSession, tenant_workflow: TenantWorkflowRead):
        """
        Initialize a new `PresentCredentialWorkflow` instance.
        """
        super(PresentCredentialWorkflow, self).__init__(db, tenant_workflow)
        self._present_repo = PresentCredentialsRepository(db_session=db)

    @property
    def present_repo(self) -> PresentCredentialsRepository:
        """Accessor for present_repo instance."""
        return self._present_repo

    async def run_step(self, webhook_message: dict = None) -> TenantWorkflowRead:
        present_cred = await self.present_repo.get_by_workflow_id(
            self.tenant_workflow.id
        )

        # if workflow is "pending" then we need to start it
        # called direct from the tenant admin api so the tenant is "in context"
        if self.tenant_workflow.workflow_state == TenantWorkflowStateType.pending:
            # update the workflow status as "in_progress"
            await self.start_workflow()

            if present_cred.present_role == PresentationRoleType.verifier:
                present_cred = await self.verifier_request_presentation(present_cred)

            elif present_cred.present_role == PresentationRoleType.holder:
                present_cred = await self.holder_present_credential(present_cred)

            else:
                # ignore for now
                pass

        # if workflow is "in_progress" we need to check what state we are at,
        # ... and initiate the next step (if applicable)
        # called on receipt of webhook, so need to put the proper tenant "in context"
        elif self.tenant_workflow.workflow_state == TenantWorkflowStateType.in_progress:
            webhook_topic = webhook_message["topic"]
            logger.debug(f">>> checking for webhook_topic: {webhook_topic}")
            if webhook_topic == WebhookTopicType.present_proof:
                # check for state of "credential_acked"
                webhook_state = webhook_message["payload"]["state"]
                logger.debug(f">>> checking for webhook_state: {webhook_state}")
                if (
                    webhook_state == PresentationStateType.presentation_received
                    or webhook_state == PresentationStateType.verified
                ):
                    present_cred = await self.complete_presentation(present_cred)

                    # finish off our workflow
                    await self.complete_workflow()

                else:
                    # just update our status
                    present_cred = await self.update_presentation_state(
                        present_cred, webhook_state
                    )

            else:
                logger.warn(f">>> ignoring topic for now: {webhook_topic}")

        # if workflow is "completed" or "error" then we are done
        else:
            pass

        return self.tenant_workflow

    async def verifier_request_presentation(
        self, present_cred: PresentCredentialRead
    ) -> PresentCredentialRead:
        proof_req = IndyProofRequest(
            requested_attributes={},
            requested_predicates={},
        )
        pres_request = V10PresentationSendRequestRequest(
            connection_id=str(present_cred.connection_id),
            proof_request=proof_req,
            comment="TBD comment goes here",
        )
        data = {"body": pres_request}
        pres_resp = pres_cred_v10_api.present_proof_send_request_post(**data)

        # add the transaction id to our tenant schema setup
        update_present = PresentCredentialUpdate(
            id=present_cred.id,
            workflow_id=self.tenant_workflow.id,
            present_state=pres_resp.state,
            pres_exch_id=pres_resp.presentation_exchange_id,
        )
        present_cred = await self.present_repo.update(update_present)
        return present_cred

    async def holder_present_credential(
        self, present_cred: PresentCredentialRead
    ) -> PresentCredentialRead:
        pres_resp = (
            pres_cred_v10_api.present_proof_records_pres_ex_id_send_presentation_post(
                str(present_cred.pres_exch_id)
            )
        )

        # add the transaction id to our tenant schema setup
        update_present = PresentCredentialUpdate(
            id=present_cred.id,
            workflow_id=self.tenant_workflow.id,
            present_state=pres_resp.state,
            pres_exch_id=pres_resp.presentation_exchange_id,
        )
        present_cred = await self.present_repo.update(update_present)
        return present_cred

    async def update_presentation_state(
        self, present_cred: PresentCredentialRead, state: str
    ) -> PresentCredentialRead:
        logger.debug(f">>> updating state to {state}")
        update_present = PresentCredentialUpdate(
            id=present_cred.id,
            workflow_id=self.tenant_workflow.id,
            present_state=state,
            pres_exch_id=present_cred.pres_exch_id,
        )
        present_cred = await self.present_repo.update(update_present)
        return present_cred

    async def complete_presentation(
        self, present_cred: PresentCredentialRead
    ) -> PresentCredentialRead:
        update_present = PresentCredentialUpdate(
            id=present_cred.id,
            workflow_id=self.tenant_workflow.id,
            present_state=present_cred.present_state,
            pres_exch_id=present_cred.pres_exch_id,
        )
        present_cred = await self.present_repo.update(update_present)
        return present_cred
