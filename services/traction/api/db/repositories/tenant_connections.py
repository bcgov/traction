from typing import List, Type
from uuid import UUID
from pydantic import parse_obj_as
from sqlalchemy import select

from api.db.errors import DoesNotExist
from api.db.models.tenant_connection import (
    TenantConnectionCreate,
    TenantConnectionUpdate,
    TenantConnectionRead,
    TenantConnection,
)
from api.db.repositories.base import BaseRepository


class TenantConnectionsRepository(
    BaseRepository[
        TenantConnectionCreate,
        TenantConnectionUpdate,
        TenantConnectionRead,
        TenantConnection,
    ]
):
    @property
    def _in_schema(self) -> Type[TenantConnectionCreate]:
        return TenantConnectionCreate

    @property
    def _upd_schema(self) -> Type[TenantConnectionUpdate]:
        return TenantConnectionUpdate

    @property
    def _schema(self) -> Type[TenantConnectionRead]:
        return TenantConnectionRead

    @property
    def _table(self) -> Type[TenantConnection]:
        return TenantConnection

    async def get_by_tenant_id(self, tenant_id: UUID) -> Type[TenantConnectionRead]:
        q = select(self._table).where(self._table.tenant_id == tenant_id)
        result = await self._db_session.execute(q)
        tenant_connection = result.scalar_one_or_none()
        if not tenant_connection:
            raise DoesNotExist(
                f"{self._table.__name__}<tenant_id:{tenant_id}> does not exist"
            )
        return self._schema.from_orm(tenant_connection)

    async def find_by_wallet_id(
        self, wallet_id: UUID, offset: int = 0, limit: int = 100
    ) -> List[TenantConnectionRead]:
        # not sure how to make this into a generic search function
        q = (
            select(self._table)
            .where(self._table.wallet_id == wallet_id)
            .offset(offset)
            .limit(limit)
        )
        result = await self._db_session.execute(q)
        items = result.scalars().all()
        return parse_obj_as(List[TenantConnectionRead], items)

    async def get_by_workflow_id(
        self, wallet_id: UUID, workflow_id: UUID
    ) -> Type[TenantConnectionRead]:
        q = (
            select(self._table)
            .where(self._table.wallet_id == wallet_id)
            .where(self._table.workflow_id == workflow_id)
        )
        result = await self._db_session.execute(q)
        tenant_connection = result.scalar_one_or_none()
        if not tenant_connection:
            raise DoesNotExist(
                f"{self._table.__name__}<workflow_id:{workflow_id}> does not exist"
            )
        return self._schema.from_orm(tenant_connection)

    async def get_by_wallet_and_connection_id(
        self, wallet_id: UUID, connection_id: UUID
    ) -> Type[TenantConnectionRead]:
        q = (
            select(self._table)
            .where(self._table.wallet_id == wallet_id)
            .where(self._table.connection_id == connection_id)
        )
        result = await self._db_session.execute(q)
        tenant_connection = result.scalar_one_or_none()
        if not tenant_connection:
            raise DoesNotExist(
                (
                    f"{self._table.__name__}<wallet_id:{wallet_id}>"
                    f"<connection_id:{connection_id}> does not exist"
                )
            )
        return self._schema.from_orm(tenant_connection)
