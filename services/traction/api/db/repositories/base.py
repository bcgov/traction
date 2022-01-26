import abc
from typing import Generic, TypeVar, Type, List
from uuid import uuid4, UUID

from pydantic import parse_obj_as
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from api.db.errors import DoesNotExist
from api.db.models.base import BaseModel

IN_SCHEMA = TypeVar("IN_SCHEMA", bound=BaseModel)
UPD_SCHEMA = TypeVar("UPD_SCHEMA", bound=BaseModel)
SCHEMA = TypeVar("SCHEMA", bound=BaseModel)
TABLE = TypeVar("TABLE")


class BaseRepository(
    Generic[IN_SCHEMA, UPD_SCHEMA, SCHEMA, TABLE], metaclass=abc.ABCMeta
):
    def __init__(self, db_session: AsyncSession, *args, **kwargs) -> None:
        self._db_session: AsyncSession = db_session

    @property
    @abc.abstractmethod
    def _table(self) -> Type[TABLE]:
        ...

    @property
    @abc.abstractmethod
    def _schema(self) -> Type[SCHEMA]:
        ...

    async def create(self, in_schema: IN_SCHEMA) -> SCHEMA:
        entry = self._table(id=uuid4(), **in_schema.dict())
        self._db_session.add(entry)
        await self._db_session.commit()
        return self._schema.from_orm(entry)

    async def update(self, upd_schema: UPD_SCHEMA) -> SCHEMA:
        stmt = (
            update(self._table)
            .where(self._table.id == upd_schema.id)
            .values(**upd_schema.dict(exclude_unset=True))
        )
        await self._db_session.execute(stmt)
        await self._db_session.commit()
        return self.get_by_id(upd_schema.id)

    async def get_by_id(self, entry_id: UUID) -> SCHEMA:
        entry = await self._db_session.get(self._table, entry_id)
        if not entry:
            raise DoesNotExist(f"{self._table.__name__}<id:{entry_id}> does not exist")
        return self._schema.from_orm(entry)

    async def find(self, offset: int = 0, limit: int = 100) -> List[SCHEMA]:
        # not sure how to make this into a generic search function
        q = select(self._table).offset(offset).limit(limit)
        result = await self._db_session.execute(q)
        items = result.scalars().all()
        return parse_obj_as(List[self._schema], items)
