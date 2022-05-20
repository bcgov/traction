import logging
from typing import List

from uuid import UUID

from sqlalchemy import select, update, desc, func
from sqlmodel.ext.asyncio.session import AsyncSession

from acapy_client import OpenApiException
from acapy_client.model.credential_definition_send_request import (
    CredentialDefinitionSendRequest,
)
from api.db.errors import DoesNotExist
from api.db.models.v1.governance import SchemaTemplate, CredentialTemplate
from api.db.repositories.tenant_issuers import TenantIssuersRepository
from api.endpoints.models.tenant_issuer import PublicDIDStateType
from api.endpoints.models.v1.errors import (
    IdNotMatchError,
    NotFoundError,
    NotAnIssuerError,
)
from api.endpoints.models.v1.governance import (
    CreateSchemaTemplatePayload,
    SchemaTemplateItem,
    CredentialTemplateItem,
    TemplateStatusType,
    SchemaTemplateListParameters,
    UpdateSchemaTemplatePayload,
    ImportSchemaTemplatePayload,
)
from acapy_client.api.endorse_transaction_api import EndorseTransactionApi
from acapy_client.api.schema_api import SchemaApi
from acapy_client.api.credential_definition_api import CredentialDefinitionApi
from acapy_client.model.schema_send_request import SchemaSendRequest

from api.api_client_utils import get_api_client
from api.protocols.v1.endorser.endorser_protocol import EndorserStateType

endorse_api = EndorseTransactionApi(api_client=get_api_client())
schema_api = SchemaApi(api_client=get_api_client())
cred_def_api = CredentialDefinitionApi(api_client=get_api_client())


logger = logging.getLogger(__name__)


async def get_public_did(
    db: AsyncSession, tenant_id: UUID, raise_error: bool | None = False
):
    issuer_repo = TenantIssuersRepository(db)
    try:
        iss = await issuer_repo.get_by_tenant_id(tenant_id)
    except DoesNotExist:
        pass

    if iss and iss.public_did_state == PublicDIDStateType.public:
        return iss.public_did
    else:
        if raise_error:
            raise NotAnIssuerError(
                code="tenant.issuer.not-allowed",
                title="Tenant is not an Issuer",
                detail="Tenant is not an Issuer and cannot write schemas or credential definitions to the ledger.",  # noqa: E501
                links=[],  # TODO: add link to make issuer
            )
        else:
            return None


def fetch_schema_from_ledger(schema_id: str):
    try:
        ledger_schema = schema_api.schemas_schema_id_get(schema_id=schema_id)
        if ledger_schema and ledger_schema.schema:
            return ledger_schema.schema
    except OpenApiException:
        pass

    return None


async def send_schema_request_task(
    db: AsyncSession, payload: CreateSchemaTemplatePayload, item: SchemaTemplateItem
):
    public_did = await get_public_did(db, item.tenant_id)
    if not public_did:
        return

    schema_request = SchemaSendRequest(
        schema_name=payload.schema_definition.schema_name,
        schema_version=payload.schema_definition.schema_version,
        attributes=payload.schema_definition.attributes,
    )
    data = {"body": schema_request}
    resp = schema_api.schemas_post(**data)
    try:
        if resp["txn"]:
            values = {
                "schema_id": resp["txn"]["meta_data"]["context"]["schema_id"],
                "transaction_id": resp["txn"]["transaction_id"],
            }
            q = (
                update(SchemaTemplate)
                .where(SchemaTemplate.schema_template_id == item.schema_template_id)
                .values(values)
            )
            await db.execute(q)
            await db.commit()
    except AttributeError:
        # we didn't create one, one exists...
        # go through the import process...
        import_payload = ImportSchemaTemplatePayload(**payload.dict())
        import_payload.schema_id = resp["sent"]["schema_id"]
        st, ct = await import_schema_template(db, item.tenant_id, None, import_payload)
        if ct:
            # we need to kick off a cred def endorsement
            await send_cred_def_request_task(
                db, item.tenant_id, ct.credential_template_id
            )


async def send_cred_def_request_task(
    db: AsyncSession, tenant_id: UUID, credential_template_id: UUID
):
    public_did = await get_public_did(db, tenant_id)
    if not public_did:
        return
    try:
        item = await CredentialTemplate.get_by_id(db, tenant_id, credential_template_id)

        cred_def_request = CredentialDefinitionSendRequest(
            schema_id=item.schema_id,
            tag=item.tag,
        )
        if item.revocation_enabled:
            cred_def_request.support_revocation = True
            cred_def_request.revocation_registry_size = item.revocation_registry_size

        data = {"body": cred_def_request}
        cred_def_response = cred_def_api.credential_definitions_post(**data)

        values = {"transaction_id": cred_def_response.txn["transaction_id"]}
        q = (
            update(CredentialTemplate)
            .where(
                CredentialTemplate.credential_template_id == item.credential_template_id
            )
            .values(values)
        )
        await db.execute(q)
        await db.commit()
    except NotFoundError:
        logger.error(
            f"No Credential Template for id<{credential_template_id}>. Cannot send request to ledger."  # noqa: E501
        )


async def list_schema_templates(
    db: AsyncSession,
    tenant_id: UUID,
    wallet_id: UUID,
    parameters: SchemaTemplateListParameters,
) -> [List[SchemaTemplateItem], int]:
    """List Schema Templates.

    Return a page of schema templates filtered by given parameters.

    Args:
      db: database session
      tenant_id: Traction ID of tenant making the call
      wallet_id: AcaPy Wallet ID for tenant
      parameters: filters for Contacts

    Returns:
      items: The page of schema templates
      total_count: Total number of items matching criteria
    """

    limit = parameters.page_size
    skip = (parameters.page_num - 1) * limit

    filters = [
        SchemaTemplate.tenant_id == tenant_id,
        SchemaTemplate.deleted == parameters.deleted,
    ]
    if parameters.status:
        filters.append(SchemaTemplate.status == parameters.status)
    if parameters.state:
        filters.append(SchemaTemplate.state == parameters.state)

    if parameters.schema_template_id:
        filters.append(
            SchemaTemplate.schema_template_id == parameters.schema_template_id
        )
    if parameters.schema_id:
        filters.append(SchemaTemplate.schema_id == parameters.schema_id)
    if parameters.name:
        filters.append(SchemaTemplate.name.contains(parameters.name))

    # build out a base query with all filters
    base_q = select(SchemaTemplate).filter(*filters)

    # get a count of ALL records matching our base query
    count_q = select([func.count()]).select_from(base_q)
    count_q_rec = await db.execute(count_q)
    total_count = count_q_rec.scalar()

    # TODO: should we raise an exception if paging is invalid?
    # ie. is negative, or starts after available records

    # add in our paging and ordering to get the result set
    results_q = (
        base_q.limit(limit).offset(skip).order_by(desc(SchemaTemplate.created_at))
    )

    results_q_recs = await db.execute(results_q)
    db_recs = results_q_recs.scalars()

    items = []
    for db_rec in db_recs:
        item = schema_template_to_item(db_rec)
        items.append(item)

    return items, total_count


async def create_schema_template(
    db: AsyncSession,
    tenant_id: UUID,
    wallet_id: UUID,
    payload: CreateSchemaTemplatePayload,
) -> (SchemaTemplateItem, CredentialTemplateItem):
    # TODO: verify / validate payload
    # check if schema name/schema version exist here and/or ledger
    public_did = await get_public_did(db, tenant_id, True)

    # KVLt4iia47yDrafuZxdxEt:2:new-aaa-002:0.0.2
    schema_id = f"{public_did}:2:{payload.schema_definition.schema_name}:{payload.schema_definition.schema_version}"  # noqa: E501
    ledger_schema = fetch_schema_from_ledger(schema_id)
    if ledger_schema:
        raise IdNotMatchError(
            code="schema_id.ledger.exists",
            title="Schema ID exists on Ledger",
            detail=f"Schema ID in payload data <{schema_id}> exists on ledger. Use import schema template",  # noqa: E501
            links=[],  # TODO: add link to import call
        )

    # create OUR schema template
    db_schema = SchemaTemplate(
        tenant_id=tenant_id,
        status=TemplateStatusType.pending,
        state=EndorserStateType.init,
        tags=payload.tags,
        name=payload.name if payload.name else payload.schema_definition.schema_name,
        attributes=payload.schema_definition.attributes,
        version=payload.schema_definition.schema_version,
        schema_name=payload.schema_definition.schema_name,
        schema_id=schema_id,
    )
    db.add(db_schema)
    await db.flush()  # need to get the schema_template_id

    # create OUR cred def template (optional)
    db_cred = None
    if payload.credential_definition and payload.credential_definition.tag:
        cd = payload.credential_definition
        if cd.revocation_enabled and cd.revocation_registry_size < 4:
            cd.revocation_registry_size = 4

        db_cred = CredentialTemplate(
            schema_template_id=db_schema.schema_template_id,
            tenant_id=tenant_id,
            status=TemplateStatusType.pending,
            state=EndorserStateType.init,
            tags=payload.tags,
            name=db_schema.name,
            attributes=db_schema.attributes,
            schema_id=db_schema.schema_id,
            tag=cd.tag,
            revocation_enabled=cd.revocation_enabled,
            revocation_registry_size=cd.revocation_registry_size,
            revocation_registry_state=EndorserStateType.init,
        )
        db.add(db_cred)

    await db.commit()

    item = schema_template_to_item(db_schema)
    c_t_item = credential_template_to_item(db_cred)

    return item, c_t_item


async def get_schema_template(
    db: AsyncSession,
    tenant_id: UUID,
    wallet_id: UUID,
    schema_template_id: UUID,
    deleted: bool | None = False,
) -> SchemaTemplateItem:
    """Get  Schema Template.

    Find and return a Traction Schema Template by ID.

    Args:
      db: database session
      tenant_id: Traction ID of tenant making the call
      wallet_id: AcaPy Wallet ID for tenant
      schema_template_id: Traction ID of Schema Template
      deleted: When True, return Schema Template if marked as deleted

    Returns: The Traction Schema Template

    Raises:
      NotFoundError: if the item cannot be found by ID and deleted flag
    """
    db_rec = await SchemaTemplate.get_by_id(db, tenant_id, schema_template_id, deleted)

    item = schema_template_to_item(db_rec)

    return item


async def update_schema_template(
    db: AsyncSession,
    tenant_id: UUID,
    wallet_id: UUID,
    schema_template_id: UUID,
    payload: UpdateSchemaTemplatePayload,
) -> SchemaTemplateItem:
    """Update  SchemaTemplate.

    Update a Traction SchemaTemplate.
    Note that not all fields can be modified. If they are present in the payload, they
    will be ignored.

    Args:
      db: database session
      tenant_id: Traction ID of tenant making the call
      wallet_id: AcaPy Wallet ID for tenant
      contact_id: Traction ID of Contact
      payload: SchemaTemplate data fields to update.

    Returns: The Traction SchemaTemplate

    Raises:
      NotFoundError: if the record cannot be found by ID and deleted flag
      IdNotMatchError: if the schema template id parameter and in payload do not match
    """
    # verify this contact exists and is not deleted...
    await SchemaTemplate.get_by_id(db, tenant_id, schema_template_id, False)

    # payload contact id must match parameter
    if schema_template_id != payload.schema_template_id:
        raise IdNotMatchError(
            code="schema_template.update.id-not-match",
            title="Schema Template ID mismatch",
            detail=f"Schema Template ID in payload <{payload.schema_template_id}> does not match Schema Template ID requested <{schema_template_id}>",  # noqa: E501
        )

    payload_dict = payload.dict()
    # payload isn't the same as the db... move fields around
    del payload_dict["schema_template_id"]

    if not payload.status:
        del payload_dict["status"]

    if not payload.name:
        del payload_dict["name"]

    q = (
        update(SchemaTemplate)
        .where(SchemaTemplate.tenant_id == tenant_id)
        .where(SchemaTemplate.schema_template_id == schema_template_id)
        .values(payload_dict)
    )
    await db.execute(q)
    await db.commit()

    return await get_schema_template(db, tenant_id, wallet_id, schema_template_id)


async def delete_schema_template(
    db: AsyncSession, tenant_id: UUID, wallet_id: UUID, schema_template_id: UUID
) -> SchemaTemplateItem:
    """Delete  SchemaTemplate.

    Delete a Traction SchemaTemplate.
    Note that deletes are "soft" in Traction. The SchemaTemplate will still exist but
    must be explicitly asked for using deleted=True parameters for Get or List.

    Args:
      db: database session
      tenant_id: Traction ID of tenant making the call
      wallet_id: AcaPy Wallet ID for tenant
      schema_template_id: Traction ID of SchemaTemplate

    Returns: The Traction SchemaTemplate

    Raises:
      NotFoundError: if the item cannot be found by ID and deleted flag
    """
    q = (
        update(SchemaTemplate)
        .where(SchemaTemplate.tenant_id == tenant_id)
        .where(SchemaTemplate.schema_template_id == schema_template_id)
        .values(
            deleted=True,
            status=TemplateStatusType.deleted,
        )
    )

    await db.execute(q)
    await db.commit()

    return await get_schema_template(
        db, tenant_id, wallet_id, schema_template_id, deleted=True
    )


async def import_schema_template(
    db: AsyncSession,
    tenant_id: UUID,
    wallet_id: UUID,
    payload: ImportSchemaTemplatePayload,
) -> (SchemaTemplateItem, CredentialTemplateItem):
    # TODO: verify / validate payload
    # check if schema name/schema version exist here and/or ledger

    ledger_schema = fetch_schema_from_ledger(payload.schema_id)

    if ledger_schema:
        # create OUR schema template
        db_schema = SchemaTemplate(
            tenant_id=tenant_id,
            status=TemplateStatusType.active,
            state=EndorserStateType.init,
            tags=payload.tags,
            imported=True,
            schema_id=ledger_schema.id,
            name=payload.name if payload.name else ledger_schema.name,
            attributes=ledger_schema.attr_names,
            version=ledger_schema.version,
            schema_name=ledger_schema.name,
        )
        db.add(db_schema)
        await db.flush()  # need to get the schema_template_id
        await db.commit()  # commit this part, in case they cannot create a cred def

        # check for public did / issuance permission
        await get_public_did(db, tenant_id, True)
        # create OUR cred def template (optional)
        db_cred = None
        if payload.credential_definition and payload.credential_definition.tag:
            cd = payload.credential_definition
            if cd.revocation_enabled and cd.revocation_registry_size < 4:
                cd.revocation_registry_size = 4

            db_cred = CredentialTemplate(
                schema_template_id=db_schema.schema_template_id,
                tenant_id=tenant_id,
                status=TemplateStatusType.pending,
                state=EndorserStateType.init,
                tags=payload.tags,
                name=db_schema.name,
                attributes=db_schema.attributes,
                schema_id=db_schema.schema_id,
                tag=cd.tag,
                revocation_enabled=cd.revocation_enabled,
                revocation_registry_size=cd.revocation_registry_size,
                revocation_registry_state=EndorserStateType.init,
            )
            db.add(db_cred)

        await db.commit()

        item = schema_template_to_item(db_schema)
        c_t_item = credential_template_to_item(db_cred)

        return item, c_t_item
    else:
        raise NotFoundError(
            code="ledger_schema.id_not_found",
            title="Schema not found",
            detail=f"Schema was not found on ledger for schema_id<{payload.schema_id}>",
        )


def schema_template_to_item(db_item: SchemaTemplate) -> SchemaTemplateItem:
    if db_item:
        return SchemaTemplateItem(**db_item.dict())
    else:
        return None


def credential_template_to_item(db_item: CredentialTemplate) -> CredentialTemplateItem:
    if db_item:
        return CredentialTemplateItem(**db_item.dict())
    else:
        return None
