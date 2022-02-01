import py
import pytest
import pytest_asyncio

from sqlalchemy.ext.asyncio import AsyncSession

from api.main import app
from api.db.session import engine
from fastapi.testclient import TestClient


@pytest_asyncio.fixture
def client() -> TestClient:
    client = TestClient(app)
    return client


@pytest_asyncio.fixture
async def test_session(client) -> AsyncSession:
    try:
        conn = await engine.connect()
        txn = await conn.begin()
        sess = AsyncSession(bind=conn)
        yield sess
    finally:
        await txn.rollback()
        await conn.close()
