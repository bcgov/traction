from typing import List, Type
from uuid import UUID
from pydantic import parse_obj_as
from sqlalchemy import select

from api.db.models.tenant_webhook import (
    TenantWebhookCreate,
    TenantWebhookUpdate,
    TenantWebhook,
)
from api.db.repositories.base import BaseRepository


class TenantWebhooksRepository(
    BaseRepository[
        TenantWebhookCreate, TenantWebhookUpdate, TenantWebhook, TenantWebhook
    ]
):
    @property
    def _in_schema(self) -> Type[TenantWebhookCreate]:
        return TenantWebhookCreate

    @property
    def _upd_schema(self) -> Type[TenantWebhookUpdate]:
        return TenantWebhookUpdate

    @property
    def _schema(self) -> Type[TenantWebhook]:
        return TenantWebhook

    @property
    def _table(self) -> Type[TenantWebhook]:
        return TenantWebhook

    async def find_by_wallet_id(
        self, wallet_id: UUID, offset: int = 0, limit: int = 100
    ) -> List[TenantWebhook]:
        # not sure how to make this into a generic search function
        q = (
            select(self._table)
            .where(self._table.wallet_id == wallet_id)
            .offset(offset)
            .limit(limit)
        )
        result = await self._db_session.execute(q)
        items = result.scalars().all()
        return parse_obj_as(List[TenantWebhook], items)
