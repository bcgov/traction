from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool

from api.core.config import settings


engine = create_async_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    echo=settings.DB_ECHO_LOG,
    echo_pool=settings.DB_ECHO_LOG,
    pool_size=20,
    poolclass=QueuePool,
)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
