from sqlalchemy.ext.asyncio import create_async_engine

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker, Query
from sqlalchemy import select

# from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from api.core.config import settings


engine = create_async_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    echo=settings.DB_ECHO_LOG,
    echo_pool=settings.DB_ECHO_LOG,
    pool_size=20,
    poolclass=QueuePool,
)


class TenantAsyncSession(AsyncSession):
    _tenant_id: UUID = None

    def begin(self, tenant_id, **kw):
        self._tenant_id = tenant_id
        return super(TenantAsyncSession, self).begin(**kw)

    def query(self, classz) -> Query:
        from api.db.models.base import TenantScopedModel

        return select(classz).filter(TenantScopedModel.tenant_id == self._tenant_id)


class TenantQuery(Query):
    _tenant_id: UUID = None

    def __init__(self, tenant_id):
        self._tenant_id = tenant_id

    def tenant(self):
        from api.db.models.base import TenantScopedModel

        return self.filter(TenantScopedModel.tenant_id == self._tenant_id)


async_session = sessionmaker(engine, class_=TenantAsyncSession, expire_on_commit=False)
