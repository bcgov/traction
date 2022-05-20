import json

from api.core.config import settings
from api.core.profile import Profile
from api.db.models.v1.governance import CredentialTemplate
from api.endpoints.models.v1.errors import NotFoundError
from api.protocols.v1.endorser import CreateCredDefProcessor


class CreateCredDefRevocationProcessor(CreateCredDefProcessor):
    def __init__(self):
        super().__init__()

    async def get_credential_template(
        self, profile: Profile, payload: dict
    ) -> CredentialTemplate:
        cred_def_id = self.get_cred_def_id(payload=payload)
        try:
            return await CredentialTemplate.get_by_cred_def_id(
                profile.db, profile.tenant_id, cred_def_id
            )
        except NotFoundError:
            return None

    async def approve_for_processing(self, profile: Profile, payload: dict) -> bool:
        # check metadata for cred def id, no schema id!
        # we only care about type 114 not 113.
        # we can grab type from data/json in the payload but for the final completion
        # we should grab it from the signature...

        has_no_schema_id = "schema_id" not in payload["meta_data"]["context"]
        has_cred_def_id = "cred_def_id" in payload["meta_data"]["context"]
        has_no_create_pending_rev_reg = (
            "create_pending_rev_reg" not in payload["meta_data"]["processing"]
        )
        has_auto_create_rev_reg = (
            "auto_create_rev_reg" in payload["meta_data"]["processing"]
        )
        data_json = json.loads(payload["messages_attach"][0]["data"]["json"])
        is_operation_type_114 = data_json and data_json["operation"]["type"] == "114"

        template = await self.get_credential_template(profile, payload)
        template_exists = template is not None

        approved = (
            has_no_schema_id
            and has_cred_def_id
            and has_no_create_pending_rev_reg
            and has_auto_create_rev_reg
            and is_operation_type_114
            and template_exists
        )

        self.logger.debug(f"approved = {approved}")
        return approved

    async def before_any(self, profile: Profile, payload: dict):
        o = await self.get_credential_template(profile, payload)

        if o:
            values = {"revocation_registry_state": payload["state"]}

            await self.update_state(payload, profile, values, o)

    async def on_transaction_acked(self, profile: Profile, payload: dict):
        # check the signature to confirm we are truly acked...
        endorser_public_did = settings.ACAPY_ENDORSER_PUBLIC_DID

        signature_json = payload["signature_response"][0]["signature"][
            endorser_public_did
        ]
        signature = json.loads(signature_json)

        is_operation_type_114 = signature["operation"]["type"] == "114"

        if is_operation_type_114:
            o = await self.get_credential_template(profile, payload)
            await self.set_active(profile, o)
