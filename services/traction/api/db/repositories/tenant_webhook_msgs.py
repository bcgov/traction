from typing import List, Type
from uuid import UUID
from pydantic import parse_obj_as
from sqlalchemy import select

from api.db.models.tenant_webhook_msg import (
    TenantWebhookMsgCreate,
    TenantWebhookMsgUpdate,
    TenantWebhookMsgRead,
    TenantWebhookMsg,
)
from api.db.repositories.base import BaseRepository


class TenantWebhookMsgsRepository(
    BaseRepository[
        TenantWebhookMsgCreate,
        TenantWebhookMsgUpdate,
        TenantWebhookMsgRead,
        TenantWebhookMsg,
    ]
):
    @property
    def _in_schema(self) -> Type[TenantWebhookMsgCreate]:
        return TenantWebhookMsgCreate

    @property
    def _upd_schema(self) -> Type[TenantWebhookMsgUpdate]:
        return TenantWebhookMsgUpdate

    @property
    def _schema(self) -> Type[TenantWebhookMsgRead]:
        return TenantWebhookMsgRead

    @property
    def _table(self) -> Type[TenantWebhookMsg]:
        return TenantWebhookMsg

    async def find_by_wallet_id(
        self, wallet_id: UUID, offset: int = 0, limit: int = 100
    ) -> List[TenantWebhookMsgRead]:
        # not sure how to make this into a generic search function
        q = (
            select(self._table)
            .where(self._table.wallet_id == wallet_id)
            .offset(offset)
            .limit(limit)
        )
        result = await self._db_session.execute(q)
        items = result.scalars().all()
        return parse_obj_as(List[TenantWebhookMsgRead], items)

    async def find_by_tenant_id(
        self, tenant_id: UUID, offset: int = 0, limit: int = 100
    ) -> List[TenantWebhookMsgRead]:
        # not sure how to make this into a generic search function
        q = (
            select(self._table)
            .where(self._table.tenant_id == tenant_id)
            .offset(offset)
            .limit(limit)
        )
        result = await self._db_session.execute(q)
        items = result.scalars().all()
        return parse_obj_as(List[TenantWebhookMsgRead], items)
