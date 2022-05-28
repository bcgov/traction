import logging
import re
from abc import ABC, abstractmethod
from enum import Enum
from re import Pattern
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.exc import DBAPIError
from starlette_context import context

from acapy_client.api.issue_credential_v1_0_api import IssueCredentialV10Api
from acapy_client.model.cred_attr_spec import CredAttrSpec
from acapy_client.model.credential_definition_send_request import (
    CredentialDefinitionSendRequest,
)
from acapy_client.model.credential_preview import CredentialPreview
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
from api.endpoints.models.v1.governance import SchemaDefinitionPayload
from acapy_client.api.endorse_transaction_api import EndorseTransactionApi
from acapy_client.api.schema_api import SchemaApi
from acapy_client.api.credential_definition_api import CredentialDefinitionApi
from acapy_client.model.schema_send_request import SchemaSendRequest

from api.api_client_utils import get_api_client

endorse_api = EndorseTransactionApi(api_client=get_api_client())
schema_api = SchemaApi(api_client=get_api_client())
cred_def_api = CredentialDefinitionApi(api_client=get_api_client())
issue_cred_v10_api = IssueCredentialV10Api(api_client=get_api_client())


class TractionTaskType(str, Enum):
    send_schema_request = "send_schema_request"
    send_cred_def_request = "send_cred_def_request"
    send_credential_offer = "send_credential_offer"


TRACTION_TASK_PREFIX = "traction::TASK::"
TRACTION_TASK_LISTENER_PATTERN = re.compile(f"^{TRACTION_TASK_PREFIX}(.*)?$")

TRACTION_SEND_SCHEMA_REQUEST_LISTENER_PATTERN = re.compile(
    f"^{TRACTION_TASK_PREFIX}{TractionTaskType.send_schema_request}(.*)?$"
)

TRACTION_SEND_CRED_DEF_REQUEST_LISTENER_PATTERN = re.compile(
    f"^{TRACTION_TASK_PREFIX}{TractionTaskType.send_cred_def_request}(.*)?$"
)

TRACTION_SEND_CREDENTIAL_OFFER_LISTENER_PATTERN = re.compile(
    f"^{TRACTION_TASK_PREFIX}{TractionTaskType.send_credential_offer}(.*)?$"
)


def get_logger(cls):
    return logging.getLogger(cls.__name__)


class Task(ABC):
    """Task (Abstract).

    The Task class is for offloading work to the event bus. There are many long running
    actions in AcaPy/Ledger etc. Use tasks to perform background work. In general, these
     tasks will call AcaPy or the ledger and the flow will be handled in protocol
    listeners as the conversations flow between the various states. Tasks will be the
    kickoff/starting point of those conversations.

    Implementing classes will specify the event bus topics and listener pattern and
    will implement the actual work (_perform_task).

    Implementing classes should create a specific class method to trigger the work.
    These methods should build the payload and call _assign (which places the task on
    the event bus).

    In this way, the Task class can provide an easy way for callers to assign the task
    to the event bus and do the work once it comes off the bus.

    To facilitate calls to AcaPy, the tenant's wallet token is added to the context
    before _perform_task is called.

    Although the event profile contains a db session object, do NOT use this. Open a
    session in _perform_task if/when needed.

    """

    def __init__(self):
        self._logger = logging.getLogger(type(self).__name__)
        self._pattern = self._listener_pattern()
        settings.EVENT_BUS.subscribe(self._pattern, self._notify)

    @staticmethod
    @abstractmethod
    def _listener_pattern() -> Pattern[str]:
        pass

    @staticmethod
    @abstractmethod
    def _event_topic() -> str:
        pass

    @property
    def logger(self):
        return self._logger

    async def _get_tenant(self, profile: Profile) -> Tenant:
        async with async_session() as db:
            q = select(Tenant).where(Tenant.id == profile.tenant_id)
            q_result = await db.execute(q)
            db_rec = q_result.scalar_one_or_none()
            return db_rec

    async def _notify(self, profile: Profile, event: Event):
        tenant = await self._get_tenant(profile)
        context["TENANT_WALLET_TOKEN"] = tenant.wallet_token
        payload = event.payload["payload"]
        await self._perform_task(tenant=tenant, payload=payload)

    @abstractmethod
    async def _perform_task(self, tenant: Tenant, payload: dict):
        pass

    @classmethod
    async def _assign(cls, tenant_id: UUID, wallet_id: UUID, payload):
        """Assign Task.

        Assign a task to be performed.
        Payload will be dependent on the task implementation

        Args:
          tenant_id: Traction ID of tenant making the call
          wallet_id: AcaPy Wallet ID for tenant
          payload: data for the task to run (parsed in _perform_task)
        """
        get_logger(cls).info("> _assign()")
        get_logger(cls).debug(f"tenant_id = {tenant_id}")
        get_logger(cls).debug(f"wallet_id = {wallet_id}")
        get_logger(cls).debug(f"payload = {payload}")
        # create the profile passed to listener/handler
        async with async_session() as db:
            # db is only to satisfy Profile requirements.
            # do NOT use this db anywhere, get a db session when needed in _perform_task
            profile = Profile(wallet_id, tenant_id, db)

        event_topic = cls._event_topic()
        get_logger(cls).debug(f"event_topic = {event_topic}")

        await profile.notify(event_topic, {"topic": "task", "payload": payload})
        get_logger(cls).info(f"< _assign()")


class SendSchemaRequestTask(Task):
    @staticmethod
    def _listener_pattern() -> Pattern[str]:
        return TRACTION_SEND_SCHEMA_REQUEST_LISTENER_PATTERN

    @staticmethod
    def _event_topic() -> str:
        return TRACTION_TASK_PREFIX + TractionTaskType.send_schema_request

    async def _perform_task(self, tenant: Tenant, payload: dict):
        self.logger.info("> _perform_task()")
        schema_definition = payload["schema_definition"]
        schema_template_id = payload["schema_template_id"]
        schema_request = SchemaSendRequest(
            schema_name=schema_definition.schema_name,
            schema_version=schema_definition.schema_version,
            attributes=schema_definition.attributes,
        )
        data = {"body": schema_request}
        self.logger.debug(f"schema_definition = {schema_definition}")
        self.logger.debug(f"schema_template_id = {schema_template_id}")
        self.logger.debug(f"data = {data}")
        self.logger.debug("> > schema_api.schemas_post()")
        resp = schema_api.schemas_post(**data)
        self.logger.debug(f"< < schema_api.schemas_post({resp})")
        try:
            if resp["txn"]:
                values = {
                    "schema_id": resp["txn"]["meta_data"]["context"]["schema_id"],
                    "transaction_id": resp["txn"]["transaction_id"],
                }
                self.logger.debug(f"update values = {values}")
                q = (
                    update(SchemaTemplate)
                    .where(SchemaTemplate.schema_template_id == schema_template_id)
                    .values(values)
                )
                async with async_session() as db:
                    try:
                        await db.execute(q)
                    except DBAPIError:
                        await db.rollback()
                        self.logger.error(exc_info=1)
                    else:
                        await db.commit()
        except AttributeError:
            self.logger.error()
        self.logger.info("< _perform_task()")

    @classmethod
    async def assign(
        cls,
        tenant_id: UUID,
        wallet_id: UUID,
        schema_definition: SchemaDefinitionPayload,
        schema_template_id: UUID,
    ):
        """Assign Send Schema Request Task.

        Send a schema request to the endorser/ledger. This assumes that all checks have
        been made that the tenant is an issuer and the schema defined is not already
        on the ledger.

        Args:
          tenant_id: Traction ID of tenant making the call
          wallet_id: AcaPy Wallet ID for tenant
          schema_definition: SchemaDefinitionPayload
          schema_template_id: UUID of schema template id
        """
        # create the profile passed to listener/handler
        get_logger(cls).info("> assign()")
        payload = {
            "schema_definition": schema_definition,
            "schema_template_id": schema_template_id,
        }
        get_logger(cls).debug(f"payload = {payload}")
        await cls._assign(tenant_id, wallet_id, payload)
        get_logger(cls).info("< assign()")


class SendCredDefRequestTask(Task):
    @staticmethod
    def _listener_pattern() -> Pattern[str]:
        return TRACTION_SEND_CRED_DEF_REQUEST_LISTENER_PATTERN

    @staticmethod
    def _event_topic() -> str:
        return TRACTION_TASK_PREFIX + TractionTaskType.send_cred_def_request

    async def _perform_task(self, tenant: Tenant, payload: dict):
        self.logger.info("> _perform_task()")
        c_t_id = payload["credential_template_id"]
        try:
            async with async_session() as db:
                item = await CredentialTemplate.get_by_id(db, tenant.id, c_t_id)

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
            self.logger.debug(f"data = {data}")
            self.logger.debug("> > cred_def_api.credential_definitions_post()")
            cred_def_response = cred_def_api.credential_definitions_post(**data)
            self.logger.debug(
                f"< < cred_def_api.credential_definitions_post({cred_def_response})"
            )

            values = {"transaction_id": cred_def_response.txn["transaction_id"]}
            self.logger.debug(f"update values = {values}")
            q = (
                update(CredentialTemplate)
                .where(CredentialTemplate.credential_template_id == c_t_id)
                .values(values)
            )
            async with async_session() as db:
                try:
                    await db.execute(q)
                except DBAPIError:
                    await db.rollback()
                    self.logger.error(exc_info=1)
                else:
                    await db.commit()
        except NotFoundError:
            self.logger.error(
                f"No Credential Template for id<{c_t_id}>. Cannot send request to ledger."  # noqa: E501
            )
        self.logger.info("< _perform_task()")

    @classmethod
    async def assign(
        cls, tenant_id: UUID, wallet_id: UUID, credential_template_id: UUID
    ):
        """Assign Cred Def Request Task.

        Send a Cred Def request to the endorser/ledger. This assumes that all checks
        have been made that the tenant is an issuer and the cred def is not already on
        the ledger.

        Args:
          tenant_id: Traction ID of tenant making the call
          wallet_id: AcaPy Wallet ID for tenant
          credential_template_id: UUID for credential template
        """
        get_logger(cls).info("> assign()")
        payload = {
            "credential_template_id": credential_template_id,
        }
        get_logger(cls).debug(f"payload = {payload}")
        await cls._assign(tenant_id, wallet_id, payload)
        get_logger(cls).info("< assign()")


class SendCredentialOfferTask(Task):
    @staticmethod
    def _listener_pattern():
        return TRACTION_SEND_CREDENTIAL_OFFER_LISTENER_PATTERN

    @staticmethod
    def _event_topic() -> str:
        return TRACTION_TASK_PREFIX + TractionTaskType.send_credential_offer

    def _credential_preview_conversion(self, item: IssuerCredential):
        if item.credential_preview and "attributes" in item.credential_preview:
            attrs = item.credential_preview["attributes"]
            cred_attrs = []
            for a in attrs:
                cred_attr = CredAttrSpec(**a)
                cred_attrs.append(cred_attr)
            return CredentialPreview(attributes=cred_attrs)

        return None

    async def _perform_task(self, tenant: Tenant, payload: dict):
        self.logger.info("> _perform_task()")
        issuer_credential_id = payload["issuer_credential_id"]
        try:
            async with async_session() as db:
                item = await IssuerCredential.get_by_id(
                    db, tenant.id, issuer_credential_id
                )
            cred_preview = self._credential_preview_conversion(item)

            cred_offer = V10CredentialFreeOfferRequest(
                connection_id=str(item.contact.connection_id),
                cred_def_id=item.credential_template.cred_def_id,
                credential_preview=cred_preview,
                comment=item.comment,
                auto_issue=True,
                auto_remove=False,
            )
            data = {"body": cred_offer}
            self.logger.debug(f"data = {data}")
            self.logger.debug("> > issue_cred_v10_api.issue_credential_send_offer_post")
            cred_response = issue_cred_v10_api.issue_credential_send_offer_post(**data)
            self.logger.debug(
                f"< < issue_cred_v10_api.issue_credential_send_offer_post({cred_response})"  # noqa: E501
            )

            values = {
                "credential_exchange_id": cred_response.credential_exchange_id,
                "thread_id": cred_response.thread_id,
            }
            if not item.preview_persisted:
                # remove the preview/attributes...
                values["credential_preview"] = {}

            self.logger.debug(f"update values = {values}")

            q = (
                update(IssuerCredential)
                .where(
                    IssuerCredential.issuer_credential_id == item.issuer_credential_id
                )
                .values(values)
            )
            async with async_session() as db:
                try:
                    await db.execute(q)
                except DBAPIError:
                    await db.rollback()
                    self.logger.error(exc_info=1)
                else:
                    await db.commit()
        except NotFoundError:
            self.logger.error(
                f"No Issuer Credential found for id<{issuer_credential_id}>. Cannot offer credential."  # noqa: E501
            )
        self.logger.info("< _perform_task()")

    @classmethod
    async def assign(cls, tenant_id: UUID, wallet_id: UUID, issuer_credential_id: UUID):
        """Assign Cred Def Request Task.

        Send a Credential Offer. The Issuer Credential will specify the Contact and
        Credential Template (connection and cred def) for the offer.

        Args:
          tenant_id: Traction ID of tenant making the call
          wallet_id: AcaPy Wallet ID for tenant
          issuer_credential_id: UUID for issuer credential to offer
        """
        get_logger(cls).info("> assign()")
        payload = {
            "issuer_credential_id": issuer_credential_id,
        }
        get_logger(cls).debug(f"payload = {payload}")
        await cls._assign(tenant_id, wallet_id, payload)
        get_logger(cls).info("< assign()")

