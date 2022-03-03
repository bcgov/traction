from typing import Type, List
from uuid import UUID

from pydantic import parse_obj_as
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from api.db.errors import DoesNotExist
from api.db.models.line_of_business import (
    LobCreate,
    LobUpdate,
    Lob,
    LobRead,
)
from api.db.models.related import LobReadWithSandbox
from api.db.repositories.base import BaseRepository


class LobRepository(BaseRepository[LobCreate, LobUpdate, LobRead, Lob]):
    @property
    def _in_schema(self) -> Type[LobCreate]:
        return LobCreate

    @property
    def _upd_schema(self) -> Type[LobUpdate]:
        return LobUpdate

    @property
    def _schema(self) -> Type[LobRead]:
        return LobRead

    @property
    def _table(self) -> Type[Lob]:
        return Lob

    async def get_by_id_with_sandbox(
        self, sandbox_id: UUID, entry_id: UUID
    ) -> LobReadWithSandbox:
        q = (
            select(self._table)
            .where(self._table.id == entry_id)
            .where(self._table.sandbox_id == sandbox_id)
            .options(selectinload(Lob.sandbox))
        )
        result = await self._db_session.execute(q)
        item = result.scalars().one_or_none()
        if not item:
            raise DoesNotExist(f"{self._table.__name__}<id:{entry_id}> does not exist")
        return LobReadWithSandbox.from_orm(item)

    async def get_by_name_with_sandbox(
        self, sandbox_id: UUID, name: str
    ) -> LobReadWithSandbox:
        q = (
            select(self._table)
            .where(self._table.name == name)
            .where(self._table.sandbox_id == sandbox_id)
            .options(selectinload(Lob.sandbox))
        )
        result = await self._db_session.execute(q)
        item = result.scalars().one_or_none()
        if not item:
            raise DoesNotExist(f"{self._table.__name__}<name:{name}> does not exist")
        return LobReadWithSandbox.from_orm(item)

    async def get_in_sandbox(self, sandbox_id: UUID) -> List[LobReadWithSandbox]:
        q = (
            select(self._table)
            .where(self._table.sandbox_id == sandbox_id)
            .options(selectinload(Lob.sandbox))
        )
        result = await self._db_session.execute(q)
        items = result.scalars().all()
        return parse_obj_as(List[LobReadWithSandbox], items)
