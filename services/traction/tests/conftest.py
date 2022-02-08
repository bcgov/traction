import pytest_asyncio
import pytest

from api.core.config import settings

from api.main import app, innkeeper_app
from api.endpoints.dependencies.db import get_db
from api.db.session import engine
from fastapi.testclient import TestClient

from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine
from sqlalchemy.orm import sessionmaker


TestingSessionLocal = sessionmaker(class_=AsyncSession, autocommit=False, bind=engine)


async def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        await db.close()


@pytest.fixture
async def client() -> TestClient:
    app.dependency_overrides[get_db] = override_get_db

    client = TestClient(app)
    return client


@pytest.fixture
async def innkeeper_client() -> TestClient:

    ## TODO: turn off router level security here..
    # dependency_overrides[OAuth2PasswordBearer] = None
    innkeeper_app.dependency_overrides[get_db] = override_get_db

    print(innkeeper_app.__dict__)
    client = TestClient(innkeeper_app)
    return client


# @pytest_asyncio.fixture
# async def test_session(client) -> AsyncSession:
#     try:
#         conn = await engine.connect()
#         txn = await conn.begin()
#         sess = AsyncSession(bind=conn)
#         yield sess
#     finally:
#         await txn.rollback()
#         await conn.close()
