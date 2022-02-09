import pytest

from pydantic_factories import ModelFactory
from api.db.models.tenant import TenantCreate
from api.db.repositories.tenants import TenantsRepository
from sqlalchemy.ext.asyncio import AsyncSession

from api.endpoints.models.innkeeper import CheckInRequest


class TenantCreateFactory(ModelFactory):
    __model__ = TenantCreate


class CheckInRequestFactory(ModelFactory):
    __model__ = CheckInRequest
