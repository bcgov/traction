from typing import Type, List
from uuid import UUID

from pydantic import parse_obj_as
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from api.db.errors import DoesNotExist
from api.db.models.sandbox import (
    TenantCreate,
    TenantUpdate,
    Tenant,
    TenantReadWithSandbox,
    TenantRead,
)
from api.db.repositories.base import BaseRepository


class TenantsRepository(
    BaseRepository[TenantCreate, TenantUpdate, TenantReadWithSandbox, Tenant]
):
    @property
    def _in_schema(self) -> Type[TenantCreate]:
        return TenantCreate

    @property
    def _upd_schema(self) -> Type[TenantUpdate]:
        return TenantUpdate

    @property
    def _schema(self) -> Type[TenantRead]:
        return TenantRead

    @property
    def _table(self) -> Type[Tenant]:
        return Tenant

    async def get_by_id(self, entry_id: UUID) -> TenantReadWithSandbox:
        q = (
            select(self._table)
            .where(self._table.id == entry_id)
            .options(selectinload(Tenant.sandbox))
        )
        result = await self._db_session.execute(q)
        item = result.scalars().one_or_none()
        if not item:
            raise DoesNotExist(f"{self._table.__name__}<id:{entry_id}> does not exist")
        return TenantReadWithSandbox.from_orm(item)

    async def get_in_sandbox(self, sandbox_id: UUID) -> List[TenantReadWithSandbox]:
        q = (
            select(self._table)
            .where(self._table.sandbox_id == sandbox_id)
            .options(selectinload(Tenant.sandbox))
        )
        result = await self._db_session.execute(q)
        items = result.scalars().all()
        return parse_obj_as(List[TenantReadWithSandbox], items)
