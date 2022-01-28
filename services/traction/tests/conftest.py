import py
import pytest

from api.main import app
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from api.core.config import settings


engine = create_async_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    echo=settings.DB_ECHO_LOG,
    connect_args={"check_same_thread": False},
)
async_session = sessionmaker(
    engine, class_=AsyncSession, autocommit=False, autoflush=False
)


@pytest.fixture(scope="session")
def client() -> TestClient:
    client = TestClient(app)
    return client


@pytest.fixture(scope="session")
def test_session() -> Session:
    try:
        db = async_session()
        yield db
    finally:
        db.close()
