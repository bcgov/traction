import json
from typing import List

from sqlalchemy import update
from starlette_context import context
from api.core.profile import Profile
from api.db.models.v1.governance import SchemaTemplate, CredentialTemplate
from api.endpoints.models.v1.errors import NotFoundError
from api.endpoints.models.v1.governance import TemplateStatusType
from api.protocols.v1.endorser.endorser_protocol import (
    DefaultEndorserProtocol,
    EndorserStateType,
)
from api.api_client_utils import get_api_client
from acapy_client.api.credential_definition_api import CredentialDefinitionApi
from api.services.v1 import governance_service

cred_def_api = CredentialDefinitionApi(api_client=get_api_client())


class CreateSchemaProcessor(DefaultEndorserProtocol):
    def __init__(self):
        super().__init__()

    def get_schema_id(self, payload: dict) -> str:
        return payload["meta_data"]["context"]["schema_id"]

    def get_transaction_id(self, payload: dict) -> str:
        return payload["transaction_id"]

    async def get_schema_template(
        self, profile: Profile, payload: dict
    ) -> SchemaTemplate:
        transaction_id = self.get_transaction_id(payload=payload)
        try:
            return await SchemaTemplate.get_by_transaction_id(
                profile.db, profile.tenant_id, transaction_id
            )
        except NotFoundError:
            return None

    async def get_credential_templates(
        self, profile: Profile, schema_template: SchemaTemplate
    ) -> List[CredentialTemplate]:
        return await CredentialTemplate.list_by_schema_template_id(
            db=profile.db,
            tenant_id=profile.tenant_id,
            schema_template_id=schema_template.schema_template_id,
            status=TemplateStatusType.pending,
        )

    async def approve_for_processing(self, profile: Profile, payload: dict) -> bool:
        has_schema_id = "schema_id" in payload["meta_data"]["context"]
        has_no_cred_def_id = "cred_def_id" not in payload["meta_data"]["context"]
        data_json = json.loads(payload["messages_attach"][0]["data"]["json"])
        is_operation_type_101 = data_json and data_json["operation"]["type"] == "101"

        template = await self.get_schema_template(profile, payload)
        template_exists = template is not None

        approved = (
            has_schema_id
            and has_no_cred_def_id
            and is_operation_type_101
            and template_exists
        )

        self.logger.debug(f"approved = {approved}")
        return approved

    async def before_any(self, profile: Profile, payload: dict):
        o = await self.get_schema_template(profile, payload)
        schema_id = self.get_schema_id(payload)
        active_states = [
            EndorserStateType.transaction_endorsed,
            EndorserStateType.transaction_acked,
        ]

        processing_states = [
            EndorserStateType.request_sent,
            EndorserStateType.request_received,
            EndorserStateType.transaction_created,
            EndorserStateType.transaction_resent,
            EndorserStateType.transaction_resent_received,
        ]

        cancelled_states = [
            EndorserStateType.transaction_cancelled,
            EndorserStateType.transaction_refused,
        ]

        if o:
            values = {"state": payload["state"], "schema_id": schema_id}

            if payload["state"] in active_states:
                values["status"] = TemplateStatusType.active

            if payload["state"] in processing_states:
                values["status"] = TemplateStatusType.in_progress

            if payload["state"] in cancelled_states:
                values["status"] = TemplateStatusType.cancelled

            stmt = (
                update(SchemaTemplate)
                .where(SchemaTemplate.schema_template_id == o.schema_template_id)
                .values(values)
            )
            await profile.db.execute(stmt)
            await profile.db.commit()

    async def on_transaction_acked(self, profile: Profile, payload: dict):
        tenant = await self.get_tenant(profile)
        context["TENANT_WALLET_TOKEN"] = tenant.wallet_token

        o = await self.get_schema_template(profile, payload)
        cred_templates = await self.get_credential_templates(profile, o)
        for c_t in cred_templates:
            await governance_service.send_cred_def_request_task(
                profile.db,
                tenant_id=c_t.tenant_id,
                credential_template_id=c_t.credential_template_id,
            )
