from typing import Type

from sqlalchemy import select

from api.db.repositories.base import BaseRepository
from api.db.tables.tenants import Tenant
from api.models.schema.tenants import InTenantSchema, TenantSchema


class TenantsRepository(BaseRepository[InTenantSchema, TenantSchema, Tenant]):
    @property
    def _in_schema(self) -> Type[InTenantSchema]:
        return InTenantSchema

    @property
    def _schema(self) -> Type[TenantSchema]:
        return TenantSchema

    @property
    def _table(self) -> Type[Tenant]:
        return Tenant

    async def get_by_name(self, name: str) -> Type[TenantSchema]:
        q = select(self._table).where(self._table.name == name)
        result = await self._db_session.execute(q)
        tenant = result.scalar_one_or_none()
        if not tenant:
            return None
        return self._schema.from_orm(tenant)
