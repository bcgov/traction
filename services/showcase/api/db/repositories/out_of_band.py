from typing import Type, List
from uuid import UUID

from pydantic import parse_obj_as
from sqlalchemy import select, or_
from sqlalchemy.orm import selectinload

from api.db.models.out_of_band import (
    OutOfBandCreate,
    OutOfBandUpdate,
    OutOfBandRead,
    OutOfBand,
)
from api.db.models.related import OutOfBandReadPopulated
from api.db.repositories.base import BaseRepository


class OutOfBandRepository(
    BaseRepository[OutOfBandCreate, OutOfBandUpdate, OutOfBandRead, OutOfBand]
):
    @property
    def _in_schema(self) -> Type[OutOfBandCreate]:
        return OutOfBandCreate

    @property
    def _upd_schema(self) -> Type[OutOfBandUpdate]:
        return OutOfBandUpdate

    @property
    def _schema(self) -> Type[OutOfBandRead]:
        return OutOfBandRead

    @property
    def _table(self) -> Type[OutOfBand]:
        return OutOfBand

    async def get_in_sandbox(self, sandbox_id: UUID) -> List[OutOfBandReadPopulated]:
        q = (
            select(self._table)
            .where(self._table.sandbox_id == sandbox_id)
            .options(selectinload(OutOfBand.sender), selectinload(OutOfBand.recipient))
        )
        result = await self._db_session.execute(q)
        items = result.scalars().all()
        return parse_obj_as(List[OutOfBandReadPopulated], items)

    async def get_by_sender(self, sender_id: UUID) -> List[OutOfBandRead]:
        q = (
            select(self._table)
            .where(self._table.sender_id == sender_id)
            .order_by(OutOfBand.created_at.desc())
        )
        result = await self._db_session.execute(q)
        items = result.scalars().all()
        return parse_obj_as(List[OutOfBandRead], items)

    async def get_by_recipient(self, recipient_id: UUID) -> List[OutOfBandRead]:
        q = (
            select(self._table)
            .where(self._table.recipient_id == recipient_id)
            .order_by(OutOfBand.created_at.desc())
        )
        result = await self._db_session.execute(q)
        items = result.scalars().all()
        return parse_obj_as(List[OutOfBandRead], items)

    async def get_for_lob(self, lob_id: UUID) -> List[OutOfBandReadPopulated]:
        q = (
            select(self._table)
            .where(
                or_(
                    self._table.recipient_id == lob_id,
                    self._table.sender_id == lob_id,
                )
            )
            .order_by(OutOfBand.created_at.desc())
        )
        result = await self._db_session.execute(q)
        items = result.scalars().all()
        return parse_obj_as(List[OutOfBandReadPopulated], items)
