from typing import List, Type
from uuid import UUID
from pydantic import parse_obj_as
from sqlalchemy import select

from api.db.models.tenant_workflow import (
    TenantWorkflowCreate,
    TenantWorkflowUpdate,
    TenantWorkflowRead,
    TenantWorkflow,
)
from api.db.repositories.base import BaseRepository


class TenantWorkflowsRepository(
    BaseRepository[
        TenantWorkflowCreate, TenantWorkflowUpdate, TenantWorkflowRead, TenantWorkflow
    ]
):
    @property
    def _in_schema(self) -> Type[TenantWorkflowCreate]:
        return TenantWorkflowCreate

    @property
    def _upd_schema(self) -> Type[TenantWorkflowUpdate]:
        return TenantWorkflowUpdate

    @property
    def _schema(self) -> Type[TenantWorkflowRead]:
        return TenantWorkflowRead

    @property
    def _table(self) -> Type[TenantWorkflow]:
        return TenantWorkflow

    async def find_by_wallet_id(
        self, wallet_id: UUID, offset: int = 0, limit: int = 100
    ) -> List[TenantWorkflowRead]:
        # not sure how to make this into a generic search function
        q = (
            select(self._table)
            .where(self._table.wallet_id == wallet_id)
            .offset(offset)
            .limit(limit)
        )
        result = await self._db_session.execute(q)
        items = result.scalars().all()
        return parse_obj_as(List[TenantWorkflowRead], items)
