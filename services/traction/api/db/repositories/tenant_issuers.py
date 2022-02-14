from typing import Type
from uuid import UUID
from sqlalchemy import select

from api.db.errors import DoesNotExist
from api.db.models.tenant_issuer import (
    TenantIssuerCreate,
    TenantIssuerUpdate,
    TenantIssuerRead,
    TenantIssuer,
)
from api.db.repositories.base import BaseRepository


class TenantIssuersRepository(
    BaseRepository[
        TenantIssuerCreate, TenantIssuerUpdate, TenantIssuerRead, TenantIssuer
    ]
):
    @property
    def _in_schema(self) -> Type[TenantIssuerCreate]:
        return TenantIssuerCreate

    @property
    def _upd_schema(self) -> Type[TenantIssuerUpdate]:
        return TenantIssuerUpdate

    @property
    def _schema(self) -> Type[TenantIssuerRead]:
        return TenantIssuerRead

    @property
    def _table(self) -> Type[TenantIssuer]:
        return TenantIssuer

    async def get_by_wallet_id(self, wallet_id: UUID) -> Type[TenantIssuerRead]:
        q = select(self._table).where(self._table.wallet_id == wallet_id)
        result = await self._db_session.execute(q)
        tenant_issuer = result.scalar_one_or_none()
        if not tenant_issuer:
            raise DoesNotExist(
                f"{self._table.__name__}<wallet_id:{wallet_id}> does not exist"
            )
        return self._schema.from_orm(tenant_issuer)
