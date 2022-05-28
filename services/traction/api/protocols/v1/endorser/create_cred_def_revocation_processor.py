import json

from api.core.config import settings
from api.core.profile import Profile
from api.db.models.v1.governance import CredentialTemplate
from api.db.session import async_session
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
            async with async_session() as db:
                return await CredentialTemplate.get_by_cred_def_id(
                    db, profile.tenant_id, cred_def_id
                )
        except NotFoundError:
            return None

    async def approve_for_processing(self, profile: Profile, payload: dict) -> bool:
        self.logger.info("> approve_for_processing()")
        # check metadata for cred def id, no schema id!
        # we only care about type 114 not 113.
        # we can grab type from data/json in the payload but for the final completion
        # we should grab it from the signature...
        self.logger.info(f"payload = {payload}")
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

        template_exists = False
        if has_cred_def_id and is_operation_type_114:
            # different transaction, so look up by cred def id
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
        self.logger.debug(f"has_no_schema_id = {has_no_schema_id}")
        self.logger.debug(f"has_cred_def_id = {has_cred_def_id}")
        self.logger.debug(
            f"has_no_create_pending_rev_reg = {has_no_create_pending_rev_reg}"
        )
        self.logger.debug(f"has_auto_create_rev_reg = {has_auto_create_rev_reg}")
        self.logger.debug(f"is_operation_type_114 = {is_operation_type_114}")
        self.logger.debug(f"template_exists = {template_exists}")
        self.logger.info(f"< approve_for_processing({approved})")
        return approved

    async def before_any(self, profile: Profile, payload: dict):
        self.logger.info("> before_any()")
        o = await self.get_credential_template(profile, payload)

        if o:
            values = {"revocation_registry_state": payload["state"]}
            self.logger.debug(f"update values = {values}")

            await self.update_state(payload, profile, values, o)
        self.logger.info("< before_any()")

    async def on_transaction_acked(self, profile: Profile, payload: dict):
        self.logger.info("> on_transaction_acked()")
        # check the signature to confirm we are truly acked...
        endorser_public_did = settings.ACAPY_ENDORSER_PUBLIC_DID
        self.logger.debug(f"endorser_public_did = {endorser_public_did}")

        signature_json = payload["signature_response"][0]["signature"][
            endorser_public_did
        ]
        signature = json.loads(signature_json)

        is_operation_type_114 = signature["operation"]["type"] == "114"
        self.logger.debug(f"is_operation_type_114 = {is_operation_type_114}")

        if is_operation_type_114:
            o = await self.get_credential_template(profile, payload)
            await self.set_active(profile, o)
        self.logger.info("< on_transaction_acked()")
