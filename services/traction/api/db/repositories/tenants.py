from typing import Type

from sqlalchemy import select

from api.db.models.tenant import TenantCreate, TenantUpdate, Tenant
from api.db.repositories.base import BaseRepository


class TenantsRepository(BaseRepository[TenantCreate, TenantUpdate, Tenant, Tenant]):
    @property
    def _in_schema(self) -> Type[TenantCreate]:
        return TenantCreate

    @property
    def _upd_schema(self) -> Type[TenantUpdate]:
        return TenantUpdate

    @property
    def _schema(self) -> Type[Tenant]:
        return Tenant

    @property
    def _table(self) -> Type[Tenant]:
        return Tenant

    async def get_by_name(self, name: str) -> Type[Tenant]:
        q = select(self._table).where(self._table.name == name)
        result = await self._db_session.execute(q)
        tenant = result.scalar_one_or_none()
        if not tenant:
            return None
        return self._schema.from_orm(tenant)
