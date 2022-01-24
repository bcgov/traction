from config import Config

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker


engine = create_async_engine(Config.SQLALCHEMY_DATABASE_URI, echo=True, future=True)
admin_engine = create_async_engine(
    Config.SQLALCHEMY_DATABASE_ADMIN_URI, echo=True, future=True
)


async def get_session() -> AsyncSession:
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session
