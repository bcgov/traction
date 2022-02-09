import pytest
import asyncio

from fastapi import FastAPI
from typing import Generator, Callable
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from api.db.session import engine, async_session

from typing import AsyncGenerator
from httpx import AsyncClient


@pytest.fixture(scope="session")
def event_loop(request) -> Generator:
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture()
async def db_session() -> AsyncSession:
    async with engine.begin() as connection:
        # await connection.run_sync(BaseModel.metadata.drop_all)
        # await connection.run_sync(BaseModel.metadata.create_all)
        async with async_session(bind=connection) as session:
            yield session
            await session.flush()
            await session.rollback()


@pytest.fixture()
def override_get_db(db_session: AsyncSession) -> Callable:
    async def _override_get_db():
        ##transaction roll per test here.
        yield db_session

    return _override_get_db


@pytest.fixture()
def test_app(override_get_db: Callable) -> FastAPI:
    from api.endpoints.dependencies.db import get_db
    from api.main import app, innkeeper_app, tenant_app, webhook_app, acapy_wrapper_app

    # override sub-app get_db
    innkeeper_app.dependency_overrides[get_db] = override_get_db
    tenant_app.dependency_overrides[get_db] = override_get_db
    webhook_app.dependency_overrides[get_db] = override_get_db
    acapy_wrapper_app.dependency_overrides[get_db] = override_get_db

    return app


@pytest_asyncio.fixture()
async def test_client(test_app: FastAPI) -> AsyncGenerator:
    async with AsyncClient(app=test_app, base_url="http://test") as ac:
        yield ac
