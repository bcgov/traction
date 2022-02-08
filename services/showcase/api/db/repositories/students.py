from typing import Type
from sqlalchemy import select

from api.db.models.student import StudentCreate, StudentUpdate, Student
from api.db.repositories.base import BaseRepository


class StudentsRepository(
    BaseRepository[StudentCreate, StudentUpdate, Student, Student]
):
    @property
    def _in_schema(self) -> Type[StudentCreate]:
        return StudentCreate

    @property
    def _upd_schema(self) -> Type[StudentUpdate]:
        return StudentUpdate

    @property
    def _schema(self) -> Type[Student]:
        return Student

    @property
    def _table(self) -> Type[Student]:
        return Student

    async def get_by_name(self, name: str) -> Type[Student]:
        q = select(self._table).where(self._table.name == name)
        result = await self._db_session.execute(q)
        student = result.scalar_one_or_none()
        if not student:
            return None
        return self._schema.from_orm(student)
