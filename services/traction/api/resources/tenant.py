from fastapi import Depends, APIRouter
from typing import Optional
from sqlalchemy import select
from sqlmodel import Session
from api.db import get_session

from api.models.tenant import Tenant, TenantCreate

router = APIRouter()

@router.get("/all", response_model=list[Tenant])
def get_all_tenants(session: Session = Depends(get_session)):
    result = session.execute(select(Tenant))
    tenants = result.scalars().all()
    return [Tenant(name=t.name, wallet_id=t.wallet_id) for t in tenants]