from typing import List, Type
from uuid import UUID
from pydantic import parse_obj_as
from sqlalchemy import select

from api.db.errors import DoesNotExist
from api.db.models.tenant_schema import (
    TenantSchemaCreate,
    TenantSchemaUpdate,
    TenantSchemaRead,
    TenantSchema,
)
from api.db.repositories.base import BaseRepository


class TenantSchemasRepository(
    BaseRepository[
        TenantSchemaCreate, TenantSchemaUpdate, TenantSchemaRead, TenantSchema
    ]
):
    @property
    def _in_schema(self) -> Type[TenantSchemaCreate]:
        return TenantSchemaCreate

    @property
    def _upd_schema(self) -> Type[TenantSchemaUpdate]:
        return TenantSchemaUpdate

    @property
    def _schema(self) -> Type[TenantSchemaRead]:
        return TenantSchemaRead

    @property
    def _table(self) -> Type[TenantSchema]:
        return TenantSchema

    async def find_by_tenant_id(
        self, tenant_id: UUID, offset: int = 0, limit: int = 100
    ) -> List[TenantSchemaRead]:
        # not sure how to make this into a generic search function
        q = (
            select(self._table)
            .where(self._table.tenant_id == tenant_id)
            .offset(offset)
            .limit(limit)
        )
        result = await self._db_session.execute(q)
        items = result.scalars().all()
        return parse_obj_as(List[TenantSchemaRead], items)

    async def find_by_wallet_id(
        self, wallet_id: UUID, offset: int = 0, limit: int = 100
    ) -> List[TenantSchemaRead]:
        # not sure how to make this into a generic search function
        q = (
            select(self._table)
            .where(self._table.wallet_id == wallet_id)
            .offset(offset)
            .limit(limit)
        )
        result = await self._db_session.execute(q)
        items = result.scalars().all()
        return parse_obj_as(List[TenantSchemaRead], items)

    async def get_by_workflow_id(self, workflow_id: UUID) -> Type[TenantSchemaRead]:
        q = select(self._table).where(self._table.workflow_id == workflow_id)
        result = await self._db_session.execute(q)
        tenant_schema = result.scalar_one_or_none()
        if not tenant_schema:
            raise DoesNotExist(
                f"{self._table.__name__}<workflow_id:{workflow_id}> does not exist"
            )
        return self._schema.from_orm(tenant_schema)

    async def get_by_transaction_id(self, txn_id: UUID) -> Type[TenantSchemaRead]:
        q = select(self._table).where(self._table.schema_txn_id == txn_id)
        result = await self._db_session.execute(q)
        tenant_schema = result.scalar_one_or_none()
        if not tenant_schema:
            q = select(self._table).where(self._table.cred_def_txn_id == txn_id)
            result = await self._db_session.execute(q)
            tenant_schema = result.scalar_one_or_none()
            if not tenant_schema:
                raise DoesNotExist(
                    f"{self._table.__name__}<transaction_id:{txn_id}> does not exist"
                )
        return self._schema.from_orm(tenant_schema)
