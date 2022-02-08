from typing import Type, List
from uuid import UUID

from pydantic import parse_obj_as
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from api.db.errors import DoesNotExist
from api.db.models.sandbox import (
    SandboxCreate,
    SandboxUpdate,
    Sandbox,
    SandboxRead,
    SandboxReadWithTenants,
)
from api.db.repositories.base import BaseRepository


class SandboxesRepository(
    BaseRepository[SandboxCreate, SandboxUpdate, SandboxRead, Sandbox]
):
    @property
    def _in_schema(self) -> Type[SandboxCreate]:
        return SandboxCreate

    @property
    def _upd_schema(self) -> Type[SandboxUpdate]:
        return SandboxUpdate

    @property
    def _schema(self) -> Type[SandboxRead]:
        return SandboxRead

    @property
    def _table(self) -> Type[Sandbox]:
        return Sandbox

    async def get_by_id(self, entry_id: UUID) -> SandboxReadWithTenants:
        q = (
            select(self._table)
            .where(self._table.id == entry_id)
            .options(selectinload(Sandbox.tenants))
        )
        result = await self._db_session.execute(q)
        item = result.scalars().one_or_none()
        if not item:
            raise DoesNotExist(f"{self._table.__name__}<id:{entry_id}> does not exist")
        return SandboxReadWithTenants.from_orm(item)

    async def find(
        self, offset: int = 0, limit: int = 100
    ) -> List[SandboxReadWithTenants]:
        q = (
            select(self._table)
            .offset(offset)
            .limit(limit)
            .options(selectinload(Sandbox.tenants))
        )
        result = await self._db_session.execute(q)
        items = result.scalars().all()
        return parse_obj_as(List[SandboxReadWithTenants], items)
