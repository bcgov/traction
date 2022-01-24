import requests
import uuid
from http import HTTPStatus

from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.db import get_session
from api.models.tenant import Tenant, TenantCreate
from api import acapy_utils as au
from config import Config


router = APIRouter()


@router.get("/", response_model=list[Tenant])
async def get_all_tenants(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Tenant))
    tenants = result.scalars().all()
    return tenants


@router.post("/", response_model=Tenant)
async def create_new_tenant(
    newTenant: TenantCreate, session: AsyncSession = Depends(get_session)
):
    tenant = Tenant(name=newTenant.name)
    # Check unique name
    if await Tenant.get_by_name(db=session, name=tenant.name):
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT, detail="name already in use"
        )

    # Call ACAPY
    url = f"{Config.ACAPY_ADMIN_URL}/multitenancy/wallet"
    data = {
        "label": newTenant.name,
        "wallet_key": str(uuid.uuid4()),
        "wallet_name": str(uuid.uuid4()),
    }
    response = requests.post(url=url, headers=au.get_acapy_headers(), json=data)
    if response.ok:
        r_json = response.json()
        # save acapy generated wallet_id
        tenant.wallet_id = r_json["wallet_id"]
        session.add(tenant)
        await session.commit()
        await session.refresh(tenant)
    else:
        return {
            "message": "Error creating tenant",
            "errors": response.text,
        }, HTTPStatus.BAD_REQUEST

    return tenant
