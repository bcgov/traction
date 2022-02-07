import pytest

from pydantic_factories import ModelFactory
from api.db.models.tenant import Tenant, TenantCreate
from api.db.repositories.tenants import TenantsRepository
from sqlalchemy.ext.asyncio import AsyncSession

from api.endpoints.models.innkeeper import CheckInRequest


class TenantFactory(ModelFactory):
    __model__ = Tenant


# def create_test_tenant(db: AsyncSession) -> TenantCreate:
#     _repo = TenantsRepository(db_session=db)
#     TenantCreate.from_orm(Tenant)
#     pass


class CheckInRequestFactory(ModelFactory):
    __model__ = CheckInRequest
