from typing import Type, List
from uuid import UUID

from pydantic import parse_obj_as
from sqlalchemy import select

from api.db.models.student import StudentCreate, StudentUpdate, StudentRead, Student
from api.db.repositories.base import BaseRepository


class StudentRepository(
    BaseRepository[StudentCreate, StudentUpdate, StudentRead, Student]
):
    @property
    def _in_schema(self) -> Type[StudentCreate]:
        return StudentCreate

    @property
    def _upd_schema(self) -> Type[StudentUpdate]:
        return StudentUpdate

    @property
    def _schema(self) -> Type[StudentRead]:
        return StudentRead

    @property
    def _table(self) -> Type[Student]:
        return Student

    async def get_by_name(self, name: str) -> Type[StudentRead]:
        q = select(self._table).where(self._table.name == name)
        result = await self._db_session.execute(q)
        student = result.scalar_one_or_none()
        if not student:
            return None
        return self._schema.from_orm(student)

    async def get_in_sandbox(self, sandbox_id: UUID) -> List[StudentRead]:
        q = select(self._table).where(self._table.sandbox_id == sandbox_id)
        result = await self._db_session.execute(q)
        items = result.scalars().all()
        return parse_obj_as(List[StudentRead], items)
