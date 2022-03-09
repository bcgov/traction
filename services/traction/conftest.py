import pytest
import asyncio

from fastapi import FastAPI
from typing import Generator, Callable
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from api.core.config import settings as s

from api.db.session import engine, async_session

from typing import AsyncGenerator
from httpx import AsyncClient


@pytest.mark.integtest
@pytest_asyncio.fixture()
async def test_client() -> AsyncGenerator:
    async with AsyncClient(base_url="http://localhost:5000") as ac:
        yield ac
