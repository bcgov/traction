import pytest
import asyncio
import os

from fastapi import FastAPI
from typing import Generator, Callable
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from api.core.config import settings as s

from api.db.session import engine, async_session

from typing import AsyncGenerator
from httpx import AsyncClient, Limits, Timeout


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
    async with AsyncClient(app=test_app, base_url="http://traction-api:5000") as ac:
        yield ac


@pytest_asyncio.fixture()
async def app_client() -> AsyncGenerator:
    limits = Limits(
        max_connections=1000, max_keepalive_connections=20, keepalive_expiry=10.0
    )
    timeout = Timeout(20.0, read=10.0)
    traction_host_url = os.environ.get("TRACTION_HOST_URL", "http://traction-api:5000")
    async with AsyncClient(
        base_url=traction_host_url, limits=limits, timeout=timeout
    ) as ac:
        yield ac
