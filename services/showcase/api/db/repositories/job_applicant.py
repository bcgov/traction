from typing import Type, List
from uuid import UUID

from pydantic import parse_obj_as
from sqlalchemy import select

from api.db.errors import DoesNotExist
from api.db.models.job_applicant import (
    ApplicantCreate,
    ApplicantUpdate,
    ApplicantRead,
    Applicant,
)
from api.db.repositories.base import BaseRepository


class ApplicantRepository(
    BaseRepository[ApplicantCreate, ApplicantUpdate, ApplicantRead, Applicant]
):
    @property
    def _in_schema(self) -> Type[ApplicantCreate]:
        return ApplicantCreate

    @property
    def _upd_schema(self) -> Type[ApplicantUpdate]:
        return ApplicantUpdate

    @property
    def _schema(self) -> Type[ApplicantRead]:
        return ApplicantRead

    @property
    def _table(self) -> Type[Applicant]:
        return Applicant

    async def get_by_alias_in_sandbox(
        self, sandbox_id: UUID, alias: str
    ) -> Type[ApplicantRead]:
        q = (
            select(self._table)
            .where(self._table.sandbox_id == sandbox_id)
            .where(self._table.alias == alias)
        )
        result = await self._db_session.execute(q)
        student = result.scalar_one_or_none()
        if not student:
            return None
        return self._schema.from_orm(student)

    async def get_by_name_in_sandbox(
        self, sandbox_id: UUID, name: str
    ) -> Type[ApplicantRead]:
        q = (
            select(self._table)
            .where(self._table.sandbox_id == sandbox_id)
            .where(self._table.name == name)
        )
        result = await self._db_session.execute(q)
        student = result.scalar_one_or_none()
        if not student:
            return None
        return self._schema.from_orm(student)

    async def get_by_id_in_sandbox(
        self, sandbox_id: UUID, applicant_id: UUID
    ) -> ApplicantRead:
        q = (
            select(self._table)
            .where(self._table.sandbox_id == sandbox_id)
            .where(self._table.id == applicant_id)
        )
        result = await self._db_session.execute(q)
        entry = result.scalars().one_or_none()
        if not entry:
            raise DoesNotExist(
                f"{self._table.__name__}<id:{applicant_id}> does not exist"
            )
        return ApplicantRead.from_orm(entry)

    async def get_in_sandbox(self, sandbox_id: UUID) -> List[ApplicantRead]:
        q = select(self._table).where(self._table.sandbox_id == sandbox_id)
        result = await self._db_session.execute(q)
        items = result.scalars().all()
        return parse_obj_as(List[ApplicantRead], items)
