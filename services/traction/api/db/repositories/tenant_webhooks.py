from typing import Type
from uuid import UUID
from sqlalchemy import select

from api.db.errors import DoesNotExist
from api.db.models.tenant_webhook import (
    TenantWebhookCreate,
    TenantWebhookUpdate,
    TenantWebhookRead,
    TenantWebhook,
)
from api.db.repositories.base import BaseRepository


class TenantWebhooksRepository(
    BaseRepository[
        TenantWebhookCreate, TenantWebhookUpdate, TenantWebhookRead, TenantWebhook
    ]
):
    @property
    def _in_schema(self) -> Type[TenantWebhookCreate]:
        return TenantWebhookCreate

    @property
    def _upd_schema(self) -> Type[TenantWebhookUpdate]:
        return TenantWebhookUpdate

    @property
    def _schema(self) -> Type[TenantWebhookRead]:
        return TenantWebhookRead

    @property
    def _table(self) -> Type[TenantWebhook]:
        return TenantWebhook

    async def get_by_tenant_id(self, tenant_id: UUID) -> Type[TenantWebhookRead]:
        q = select(self._table).where(self._table.tenant_id == tenant_id)
        result = await self._db_session.execute(q)
        item = result.scalar_one_or_none()
        if not item:
            raise DoesNotExist(
                f"{self._table.__name__}<tenant_id:{tenant_id}> does not exist"
            )
        return self._schema.from_orm(item)
