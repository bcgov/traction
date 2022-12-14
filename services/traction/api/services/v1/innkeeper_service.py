import logging
import uuid
from typing import List
from uuid import UUID

from api.core.config import settings
from api.core.profile import Profile
from api.db.errors import AlreadyExists
from api.db.models import Tenant
from api.db.models.v1.tenant_permissions import TenantPermissions
from api.db.repositories.tenants import TenantsRepository
from api.db.session import async_session
from api.endpoints.models.v1.errors import IdNotMatchError
from api.endpoints.models.v1.innkeeper import (
    TenantPermissionsItem,
    UpdateTenantPermissionsPayload,
    CheckInItem,
    CheckInPayload,
    TenantListParameters,
)

from acapy_client.model.create_wallet_request import CreateWalletRequest

from api.endpoints.models.v1.tenant import TenantItem

from api.jobs import EndorserConnectionJob, RegisterPublicDidJob, MakeIssuerJob
from api.services.v1 import tenant_service
from api.services.v1.acapy_service import multitenancy_api

logger = logging.getLogger(__name__)


def tenant_permissions_to_item(db_item: TenantPermissions) -> TenantPermissionsItem:
    item = TenantPermissionsItem(**db_item.dict())
    return item


async def get_tenant_permissions(
    tenant_id: UUID,
) -> TenantPermissionsItem:

    async with async_session() as db:
        db_item = await TenantPermissions.get_by_id(db, tenant_id)

    item = tenant_permissions_to_item(db_item)
    return item


async def update_tenant_permissions(
    tenant_id: UUID,
    payload: UpdateTenantPermissionsPayload,
) -> TenantPermissionsItem:

    async with async_session() as db:
        await TenantPermissions.get_by_id(db, tenant_id)

    # payload tenant id must match parameter
    if tenant_id != payload.tenant_id:
        raise IdNotMatchError(
            code="tenant_permissions.update.id-not-match",
            title="Tenant Permissions ID mismatch",
            detail=f"Tenant ID in payload <{payload.tenant_id}> does not match Tenant ID requested <{tenant_id}>",  # noqa: E501
        )

    payload_dict = payload.dict(exclude_unset=True)
    # payload isn't the same as the db... move fields around
    del payload_dict["tenant_id"]
    # update it...
    await TenantPermissions.update_by_id(tenant_id, payload_dict)

    return await get_tenant_permissions(tenant_id)


async def register_tenant_jobs(
    tenant_id: UUID, wallet_id: UUID, payload: CheckInPayload
):
    if payload.allow_issue_credentials:
        # make issuer implies public_did flow too...
        return await make_issuer(tenant_id)


async def check_in_tenant(payload: CheckInPayload) -> CheckInItem:
    async with async_session() as db:
        tenant_repo = TenantsRepository(db_session=db)
        existing = await tenant_repo.get_by_name(payload.name)

    if existing:
        raise AlreadyExists(f"Tenant already exists with name '{existing.name}'")

    # Call ACAPY
    wallet_key = str(uuid.uuid4())
    wallet_name = str(uuid.uuid4())
    webhook_url = settings.TRACTION_TENANT_WEBHOOK_URL
    if settings.ACAPY_WEBHOOK_URL_API_KEY and 0 < len(
        settings.ACAPY_WEBHOOK_URL_API_KEY
    ):
        webhook_url = f"{webhook_url}#{settings.ACAPY_WEBHOOK_URL_API_KEY}"
        data = {
            "label": payload.name,
            "wallet_key": wallet_key,
            "wallet_name": wallet_name,
            "wallet_type": settings.ACAPY_WALLET_TYPE,
            "wallet_dispatch_type": "default",
            "wallet_webhook_urls": [
                webhook_url,
            ],
        }
        wallet_request = CreateWalletRequest(**data)
        wallet_response = multitenancy_api.multitenancy_wallet_post(
            **{"body": wallet_request}
        )
        if wallet_response:
            # save acapy generated wallet_id
            wallet_id = wallet_response.wallet_id
            tenant = Tenant(
                **payload.dict(),
                is_active=True,
                wallet_id=wallet_id,
            )
            async with async_session() as db:
                db.add(tenant)
                await db.commit()

            await register_tenant_jobs(tenant.id, tenant.wallet_id, payload)

            return CheckInItem(
                tenant_id=tenant.id,
                name=tenant.name,
                wallet_id=tenant.wallet_id,
                wallet_key=wallet_key,
            )
        else:
            # what to return or throw here?
            return
    else:
        # improperly configured... what to return or throw here?
        return


async def make_issuer(tenant_id: UUID) -> TenantItem:
    # lets update their permissions so they can act like an issuer
    # TODO: will we need permissions if we have flows? they have to be approved...
    perms = UpdateTenantPermissionsPayload(
        tenant_id=tenant_id,
        endorser_approval=True,
        create_schema_templates=True,
        create_credential_templates=True,
        issue_credentials=True,
    )
    await update_tenant_permissions(tenant_id, perms)

    async with async_session() as db:
        tenant_repo = TenantsRepository(db_session=db)
        db_tenant = await tenant_repo.get_by_id(tenant_id)

    profile = Profile(tenant_id=tenant_id, wallet_id=db_tenant.wallet_id, db=None)
    # set the jobs to approved, let tenant kick them off
    endorser_job = EndorserConnectionJob(profile)
    await endorser_job.approve()
    did_job = RegisterPublicDidJob(profile)
    await did_job.approve()
    issuer_job = MakeIssuerJob(profile)
    await issuer_job.approve()

    issuer = await tenant_service.get_tenant(tenant_id, db_tenant.wallet_id)
    return issuer


def parameter_filter_match(param_value, value) -> bool:
    # if parameter values is set, then better check it
    if param_value is not None:
        return param_value == value
    # else let it pass (didn't want to filter on this...)
    return True


def list_tenant_filter_match(params: TenantListParameters, tenant: TenantItem) -> bool:
    return (
        parameter_filter_match(params.deleted, tenant.deleted)
        and parameter_filter_match(params.issuer, tenant.issuer)
        and parameter_filter_match(params.issuer_status, tenant.issuer_status)
        and parameter_filter_match(params.public_did_status, tenant.public_did_status)
    )


async def list_tenants(
    parameters: TenantListParameters,
) -> [List[TenantItem], int]:

    limit = parameters.page_size
    skip = (parameters.page_num - 1) * limit
    logger.info(f"parameters = {parameters}")
    logger.info(f"limit = {limit}, skip={skip}")
    # TODO: implement tenant listing properly
    async with async_session() as db:
        tenant_repo = TenantsRepository(db_session=db)
        # just grab them all and build our list out manually
        db_tenants = await tenant_repo.find(0, 999999999)

    logger.info(len(db_tenants))

    filtered_results = []
    for db_tenant in db_tenants:
        tenant = await tenant_service.get_tenant(
            db_tenant.id, db_tenant.wallet_id, parameters.deleted
        )
        if list_tenant_filter_match(parameters, tenant):
            filtered_results.append(tenant)

    return filtered_results[skip : (skip + limit)], len(filtered_results)


async def get_tenant(tenant_id: UUID) -> TenantItem:
    async with async_session() as db:
        tenant_repo = TenantsRepository(db_session=db)
        db_tenant = await tenant_repo.get_by_id(tenant_id)

    tenant = await tenant_service.get_tenant(db_tenant.id, db_tenant.wallet_id)
    return tenant
