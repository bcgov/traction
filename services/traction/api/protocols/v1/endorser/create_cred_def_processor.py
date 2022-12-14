import json

from sqlalchemy import update

from api.core.config import settings
from api.core.profile import Profile
from api.db.models.v1.governance import CredentialTemplate
from api.db.session import async_session
from api.endpoints.models.v1.errors import NotFoundError
from api.endpoints.models.v1.governance import TemplateStatusType
from api.endpoints.models.webhooks import TenantEventTopicType, TRACTION_EVENT_PREFIX
from api.protocols.v1.endorser.endorser_protocol import (
    DefaultEndorserProtocol,
    processing_states,
    cancelled_states,
)


class CreateCredDefProcessor(DefaultEndorserProtocol):
    def __init__(self):
        super().__init__()

    def get_schema_id(self, payload: dict) -> str:
        try:
            return payload["meta_data"]["context"]["schema_id"]
        except KeyError:
            return None

    def get_transaction_id(self, payload: dict) -> str:
        try:
            return payload["transaction_id"]
        except KeyError:
            return None

    def get_signature(self, payload: dict) -> dict:
        endorser_public_did = settings.ACAPY_ENDORSER_PUBLIC_DID
        self.logger.debug(f"endorser_public_did = {endorser_public_did}")
        signature_json = payload["signature_response"][0]["signature"][
            endorser_public_did
        ]
        signature = json.loads(signature_json)
        return signature

    async def get_credential_template(
        self, profile: Profile, payload: dict
    ) -> CredentialTemplate:
        transaction_id = self.get_transaction_id(payload=payload)
        try:
            async with async_session() as db:
                return await CredentialTemplate.get_by_transaction_id(
                    db, profile.tenant_id, transaction_id
                )
        except NotFoundError:
            return None

    async def approve_for_processing(self, profile: Profile, payload: dict) -> bool:
        self.logger.info("> approve_for_processing()")
        has_schema_id = "schema_id" in payload["meta_data"]["context"]
        try:
            data_json = json.loads(payload["messages_attach"][0]["data"]["json"])
        except TypeError:
            data_json = payload["messages_attach"][0]["data"]["json"]
        is_operation_type_102 = data_json and data_json["operation"]["type"] == "102"

        template = await self.get_credential_template(profile, payload)
        template_exists = template is not None

        approved = has_schema_id and is_operation_type_102 and template_exists
        self.logger.debug(f"has_schema_id={has_schema_id}")
        self.logger.debug(f"is_operation_type_102={is_operation_type_102}")
        self.logger.debug(f"template_exists={template_exists}")
        self.logger.info(f"< approve_for_processing({approved})")
        return approved

    async def before_any(self, profile: Profile, payload: dict):
        self.logger.info("> before_any()")
        o = await self.get_credential_template(profile, payload)
        schema_id = self.get_schema_id(payload)
        self.logger.debug(f"credential_template = {o}")
        self.logger.debug(f"schema_id = {schema_id}")

        if o:
            values = {
                "state": payload["state"],
                "schema_id": schema_id,
            }
            self.logger.debug(f"update values = {values}")
            await self.update_state(payload, profile, values, o)

        self.logger.info("< before_any()")

    async def on_transaction_acked(self, profile: Profile, payload: dict):
        self.logger.info("> on_transaction_acked()")
        item = await self.get_credential_template(profile, payload)

        # it is here that we get the cred def id...
        # pull it out of the signature
        signature = self.get_signature(payload)
        public_did = signature["identifier"]
        sig_type = signature["operation"]["signature_type"]
        schema_ref = signature["operation"]["ref"]
        tag = signature["operation"]["tag"]

        cred_def_id = f"{public_did}:3:{sig_type}:{schema_ref}:{tag}"

        values = {"cred_def_id": cred_def_id}
        if not item.revocation_enabled:
            # set Status to Active if we are not allowing revocation
            # otherwise, the revocation processor will set active when appropriate
            values["status"] = TemplateStatusType.active

        self.logger.debug(f"update values = {values}")

        stmt = (
            update(CredentialTemplate)
            .where(
                CredentialTemplate.credential_template_id == item.credential_template_id
            )
            .values(values)
        )
        async with async_session() as db:
            await db.execute(stmt)
            await db.commit()

        if not item.revocation_enabled:
            # set Status to Active if we are not allowing revocation
            # otherwise, the revocation processor will set active when appropriate
            await self.set_active(profile, payload)

        self.logger.info("< on_transaction_acked()")

    async def update_state(self, payload, profile, values, item):
        self.logger.info("> update_state()")
        if payload["state"] in processing_states:
            values["status"] = TemplateStatusType.in_progress
        if payload["state"] in cancelled_states:
            values["status"] = TemplateStatusType.cancelled
        self.logger.debug(f"update values = {values}")
        stmt = (
            update(CredentialTemplate)
            .where(
                CredentialTemplate.credential_template_id == item.credential_template_id
            )
            .values(values)
        )
        async with async_session() as db:
            await db.execute(stmt)
            await db.commit()
        self.logger.info("< update_state()")

    async def set_active(self, profile, payload):
        self.logger.info("> set_active()")
        item = await self.get_credential_template(profile, payload)
        values = {"status": TemplateStatusType.active}
        self.logger.debug(f"update values = {values}")
        stmt = (
            update(CredentialTemplate)
            .where(
                CredentialTemplate.credential_template_id == item.credential_template_id
            )
            .values(values)
        )
        async with async_session() as db:
            await db.execute(stmt)
            await db.commit()

        # we are able to use this cred def now, notify tenant
        await self.push_notification(profile, payload)
        self.logger.info("< set_active()")

    async def push_notification(self, profile: Profile, payload: dict):
        self.logger.info("> push_notification")
        item = await self.get_credential_template(profile, payload)
        topic = TenantEventTopicType.cred_def
        event_topic = TRACTION_EVENT_PREFIX + topic
        # TODO: what should be in this payload?
        payload = {
            "status": item.status,
            "schema_template_id": str(item.schema_template_id),
            "schema_id": str(item.schema_id),
            "credential_template_id": str(item.credential_template_id),
            "cred_def_id": item.cred_def_id,
            "state": item.state,
            "tag": item.tag,
        }
        self.logger.info(f"profile.notify(topic={event_topic}, payload={payload})")
        await profile.notify(event_topic, {"topic": topic, "payload": payload})
        self.logger.info("< push_notification")
