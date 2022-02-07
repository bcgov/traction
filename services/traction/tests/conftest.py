from typing import Sequence
import py
import pytest
import pytest_asyncio
from sqlalchemy import false
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer

from sqlalchemy.ext.asyncio import AsyncSession

from api.main import app, innkeeper_app
from api.db.session import engine
from fastapi.testclient import TestClient
from fastapi import APIRouter, Depends, FastAPI, HTTPException, status
from api.endpoints.routes.innkeeper import router as innkeeper_router


@pytest_asyncio.fixture
def client() -> TestClient:
    client = TestClient(app)
    return client


@pytest_asyncio.fixture
def innkeeper_client() -> TestClient:
    print(innkeeper_app.__dict__)
    ## TODO: turn off router level security here..
    # dependency_overrides[OAuth2PasswordBearer] = None

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
