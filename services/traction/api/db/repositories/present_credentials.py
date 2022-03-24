from typing import List, Type
from uuid import UUID
from pydantic import parse_obj_as
from sqlalchemy import select

from api.db.errors import DoesNotExist
from api.db.models.present_credential import (
    PresentCredentialCreate,
    PresentCredentialUpdate,
    PresentCredentialRead,
    PresentCredential,
)
from api.db.repositories.base import BaseRepository


class PresentCredentialsRepository(
    BaseRepository[
        PresentCredentialCreate,
        PresentCredentialUpdate,
        PresentCredentialRead,
        PresentCredential,
    ]
):
    @property
    def _in_schema(self) -> Type[PresentCredentialCreate]:
        return PresentCredentialCreate

    @property
    def _upd_schema(self) -> Type[PresentCredentialUpdate]:
        return PresentCredentialUpdate

    @property
    def _schema(self) -> Type[PresentCredentialRead]:
        return PresentCredentialRead

    @property
    def _table(self) -> Type[PresentCredential]:
        return PresentCredential

    async def find_by_tenant_id(
        self, tenant_id: UUID, offset: int = 0, limit: int = 100
    ) -> List[PresentCredentialRead]:
        # not sure how to make this into a generic search function
        q = (
            select(self._table)
            .where(self._table.tenant_id == tenant_id)
            .offset(offset)
            .limit(limit)
        )
        result = await self._db_session.execute(q)
        items = result.scalars().all()
        return parse_obj_as(List[PresentCredentialRead], items)

    async def find_by_wallet_id(
        self, wallet_id: UUID, offset: int = 0, limit: int = 100
    ) -> List[PresentCredentialRead]:
        # not sure how to make this into a generic search function
        q = (
            select(self._table)
            .where(self._table.wallet_id == wallet_id)
            .offset(offset)
            .limit(limit)
        )
        result = await self._db_session.execute(q)
        items = result.scalars().all()
        return parse_obj_as(List[PresentCredentialRead], items)

    async def find_by_wallet_id_and_role(
        self, wallet_id: UUID, role: str, offset: int = 0, limit: int = 100
    ) -> List[PresentCredentialRead]:
        # not sure how to make this into a generic search function
        q = (
            select(self._table)
            .where(self._table.wallet_id == wallet_id)
            .where(self._table.present_role == role)
            .offset(offset)
            .limit(limit)
        )
        result = await self._db_session.execute(q)
        items = result.scalars().all()
        return parse_obj_as(List[PresentCredentialRead], items)

    async def get_by_workflow_id(
        self, wallet_id: UUID, workflow_id: UUID
    ) -> Type[PresentCredentialRead]:
        q = (
            select(self._table)
            .where(self._table.wallet_id == wallet_id)
            .where(self._table.workflow_id == workflow_id)
        )
        result = await self._db_session.execute(q)
        present_cred = result.scalar_one_or_none()
        if not present_cred:
            raise DoesNotExist(
                f"{self._table.__name__}<workflow_id:{workflow_id}> does not exist"
            )
        return self._schema.from_orm(present_cred)

    async def get_by_pres_exch_id(
        self, wallet_id: UUID, pres_exch_id: UUID
    ) -> Type[PresentCredentialRead]:
        q = (
            select(self._table)
            .where(self._table.wallet_id == wallet_id)
            .where(self._table.pres_exch_id == pres_exch_id)
        )
        result = await self._db_session.execute(q)
        present_cred = result.scalar_one_or_none()
        if not present_cred:
            raise DoesNotExist(
                f"{self._table.__name__}<pres_exch_id:{pres_exch_id}> does not exist"
            )
        return self._schema.from_orm(present_cred)
