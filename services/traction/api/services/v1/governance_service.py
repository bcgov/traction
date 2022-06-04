import logging
from typing import List

from uuid import UUID

from sqlalchemy import select, update, desc, func
from sqlmodel.ext.asyncio.session import AsyncSession

from acapy_client import OpenApiException
from api.db.models.v1.governance import SchemaTemplate, CredentialTemplate
from api.endpoints.models.v1.errors import (
    IdNotMatchError,
    NotFoundError,
    AlreadyExistsError,
)
from api.endpoints.models.v1.governance import (
    CreateSchemaTemplatePayload,
    SchemaTemplateItem,
    CredentialTemplateItem,
    TemplateStatusType,
    SchemaTemplateListParameters,
    UpdateSchemaTemplatePayload,
    ImportSchemaTemplatePayload,
    CredentialTemplateListParameters,
    CreateCredentialTemplatePayload,
    UpdateCredentialTemplatePayload,
)
from acapy_client.api.endorse_transaction_api import EndorseTransactionApi
from acapy_client.api.schema_api import SchemaApi
from acapy_client.api.credential_definition_api import CredentialDefinitionApi

from api.api_client_utils import get_api_client
from api.protocols.v1.endorser.endorser_protocol import EndorserStateType
from api.services.v1 import tenant_service

endorse_api = EndorseTransactionApi(api_client=get_api_client())
schema_api = SchemaApi(api_client=get_api_client())
cred_def_api = CredentialDefinitionApi(api_client=get_api_client())


logger = logging.getLogger(__name__)


def fetch_schema_from_ledger(schema_id: str):
    try:
        ledger_schema = schema_api.schemas_schema_id_get(schema_id=schema_id)
        if ledger_schema and ledger_schema.schema:
            return ledger_schema.schema
    except OpenApiException:
        pass

    return None


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
      parameters: filters for schema templates

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
    public_did = await tenant_service.is_issuer(tenant_id, wallet_id, True)

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
    if payload.credential_definition and payload.credential_definition.tag:
        # check for public did / issuance permission
        await tenant_service.is_issuer(tenant_id, wallet_id, True)

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
        raise_schema_id_not_on_ledger(payload.schema_id)


async def list_credential_templates(
    db: AsyncSession,
    tenant_id: UUID,
    wallet_id: UUID,
    parameters: CredentialTemplateListParameters,
) -> [List[CredentialTemplateItem], int]:
    """List Credential Templates.

    Return a page of Credential templates filtered by given parameters.

    Args:
      db: database session
      tenant_id: Traction ID of tenant making the call
      wallet_id: AcaPy Wallet ID for tenant
      parameters: filters for Credential Templates

    Returns:
      items: The page of schema templates
      total_count: Total number of items matching criteria
    """

    limit = parameters.page_size
    skip = (parameters.page_num - 1) * limit

    filters = [
        CredentialTemplate.tenant_id == tenant_id,
        CredentialTemplate.deleted == parameters.deleted,
    ]
    if parameters.status:
        filters.append(CredentialTemplate.status == parameters.status)
    if parameters.state:
        filters.append(CredentialTemplate.state == parameters.state)

    if parameters.credential_template_id:
        filters.append(
            CredentialTemplate.credential_template_id
            == parameters.credential_template_id
        )
    if parameters.cred_def_id:
        filters.append(CredentialTemplate.cred_def_id == parameters.cred_def_id)

    if parameters.schema_template_id:
        filters.append(
            CredentialTemplate.schema_template_id == parameters.schema_template_id
        )
    if parameters.schema_id:
        filters.append(CredentialTemplate.schema_id == parameters.schema_id)

    if parameters.name:
        filters.append(CredentialTemplate.name.contains(parameters.name))

    # build out a base query with all filters
    base_q = select(CredentialTemplate).filter(*filters)

    # get a count of ALL records matching our base query
    count_q = select([func.count()]).select_from(base_q)
    count_q_rec = await db.execute(count_q)
    total_count = count_q_rec.scalar()

    # TODO: should we raise an exception if paging is invalid?
    # ie. is negative, or starts after available records

    # add in our paging and ordering to get the result set
    results_q = (
        base_q.limit(limit).offset(skip).order_by(desc(CredentialTemplate.created_at))
    )

    results_q_recs = await db.execute(results_q)
    db_recs = results_q_recs.scalars()

    items = []
    for db_rec in db_recs:
        item = credential_template_to_item(db_rec)
        items.append(item)

    return items, total_count


async def create_credential_template(
    db: AsyncSession,
    tenant_id: UUID,
    wallet_id: UUID,
    payload: CreateCredentialTemplatePayload,
) -> CredentialTemplateItem:
    # TODO: verify / validate payload
    await tenant_service.is_issuer(tenant_id, wallet_id, True)

    schema_template = None
    if payload.schema_template_id:
        schema_template = await SchemaTemplate.get_by_id(
            db, tenant_id, payload.schema_template_id
        )

    elif payload.schema_id:
        ledger_schema = fetch_schema_from_ledger(payload.schema_id)
        if not ledger_schema:
            # schema id not on ledger...
            raise_schema_id_not_on_ledger(payload.schema_id)

        try:
            schema_template = await SchemaTemplate.get_by_schema_id(
                db, tenant_id, payload.schema_id
            )
        except NotFoundError:
            # not in traction, import it..
            import_payload = ImportSchemaTemplatePayload(schema_id=payload.schema_id)
            await import_schema_template(db, tenant_id, wallet_id, import_payload)
            schema_template = await SchemaTemplate.get_by_schema_id(
                db, tenant_id, payload.schema_id
            )

    # create OUR credential template
    cd = payload.credential_definition
    if cd.revocation_enabled and cd.revocation_registry_size < 4:
        cd.revocation_registry_size = 4

    # see if cd tag already exists
    exists = await CredentialTemplate.get_by_schema_and_tag(
        db, tenant_id, schema_template.schema_id, cd.tag
    )
    if exists:
        raise AlreadyExistsError(
            code="credential_template.tag.in-use",
            title="Tag in use",
            detail=f"Tag <{cd.tag}> already in used for schema_id<{schema_template.schema_id}>. Use different tag for new Credential Template",  # noqa: E501
        )

    db_item = CredentialTemplate(
        schema_template_id=schema_template.schema_template_id,
        tenant_id=tenant_id,
        status=TemplateStatusType.pending,
        state=EndorserStateType.init,
        tags=payload.tags,
        name=payload.name if payload.name else schema_template.name,
        attributes=schema_template.attributes,
        schema_id=schema_template.schema_id,
        tag=cd.tag,
        revocation_enabled=cd.revocation_enabled,
        revocation_registry_size=cd.revocation_registry_size,
        revocation_registry_state=EndorserStateType.init,
    )
    db.add(db_item)

    await db.commit()

    item = credential_template_to_item(db_item)

    return item


async def get_credential_template(
    db: AsyncSession,
    tenant_id: UUID,
    wallet_id: UUID,
    credential_template_id: UUID,
    deleted: bool | None = False,
) -> CredentialTemplateItem:
    """Get  Credential Template.

    Find and return a Traction Credential Template by ID.

    Args:
      db: database session
      tenant_id: Traction ID of tenant making the call
      wallet_id: AcaPy Wallet ID for tenant
      credential_template_id: Traction ID of Credential Template
      deleted: When True, return Credential Template if marked as deleted

    Returns: The Credential Schema Template

    Raises:
      NotFoundError: if the item cannot be found by ID and deleted flag
    """
    db_rec = await CredentialTemplate.get_by_id(
        db, tenant_id, credential_template_id, deleted
    )

    item = credential_template_to_item(db_rec)

    return item


async def update_credential_template(
    db: AsyncSession,
    tenant_id: UUID,
    wallet_id: UUID,
    credential_template_id: UUID,
    payload: UpdateCredentialTemplatePayload,
) -> CredentialTemplateItem:
    """Update  CredentialTemplate.

    Update a Traction SchemaTemplate.

    Note that not all fields can be modified. If they are present in the payload,
    they will be ignored.

    Args:
      db: database session
      tenant_id: Traction ID of tenant making the call
      wallet_id: AcaPy Wallet ID for tenant
      credential_template_id: Traction ID of CredentialTemplate
      payload: CredentialTemplate data fields to update.

    Returns: The Traction CredentialTemplateItem

    Raises:
      NotFoundError: if the record cannot be found by ID and deleted flag
      IdNotMatchError: if the credential template id parameter and in payload do not
        match
    """
    # verify this contact exists and is not deleted...
    await CredentialTemplate.get_by_id(db, tenant_id, credential_template_id, False)

    # payload contact id must match parameter
    if credential_template_id != payload.credential_template_id:
        raise IdNotMatchError(
            code="credential_template.update.id-not-match",
            title="Credential Template ID mismatch",
            detail=f"Credential Template ID in payload <{payload.credential_template_id}> does not match Credential Template ID requested <{credential_template_id}>",  # noqa: E501
        )

    payload_dict = payload.dict()
    # payload isn't the same as the db... move fields around
    del payload_dict["credential_template_id"]

    if not payload.status:
        del payload_dict["status"]

    if not payload.name:
        del payload_dict["name"]

    q = (
        update(CredentialTemplate)
        .where(CredentialTemplate.tenant_id == tenant_id)
        .where(CredentialTemplate.credential_template_id == credential_template_id)
        .values(payload_dict)
    )
    await db.execute(q)
    await db.commit()

    return await get_credential_template(
        db, tenant_id, wallet_id, credential_template_id
    )


async def delete_credential_template(
    db: AsyncSession, tenant_id: UUID, wallet_id: UUID, credential_template_id: UUID
) -> CredentialTemplateItem:
    """Delete  CredentialTemplate.

    Delete a Traction CredentialTemplate.
    Note that deletes are "soft" in Traction. The CredentialTemplate will still exist
    but must be explicitly asked for using deleted=True parameters for Get or List.

    Args:
      db: database session
      tenant_id: Traction ID of tenant making the call
      wallet_id: AcaPy Wallet ID for tenant
      credential_template_id: Traction ID of CredentialTemplate

    Returns: The Traction CredentialTemplateItem

    Raises:
      NotFoundError: if the item cannot be found by ID and deleted flag
    """
    q = (
        update(CredentialTemplate)
        .where(CredentialTemplate.tenant_id == tenant_id)
        .where(CredentialTemplate.credential_template_id == credential_template_id)
        .values(
            deleted=True,
            status=TemplateStatusType.deleted,
        )
    )

    await db.execute(q)
    await db.commit()

    return await get_credential_template(
        db, tenant_id, wallet_id, credential_template_id, deleted=True
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


def raise_schema_id_not_on_ledger(schema_id):
    raise NotFoundError(
        code="ledger_schema.id_not_found",
        title="Schema not found",
        detail=f"Schema was not found on ledger for schema_id<{schema_id}>",
    )
