import pytest
import json
import asyncio

import pprint
from tests.db.tenant_factory import CheckInRequestFactory
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.testclient import TestClient

from httpx import AsyncClient

pp = pprint.PrettyPrinter()
pytestmark = pytest.mark.asyncio


async def test_tenants_get_all(
    innkeeper_client: AsyncClient, db_session: AsyncSession
) -> None:
    # ARRANGE
    print(hex(id(asyncio.get_event_loop())))

    create_checkin_body = CheckInRequestFactory.build()
    resp = await innkeeper_client.post("/v1/check-in", json=create_checkin_body.dict())
    assert resp.status_code == 201, resp.content

    # ACT
    resp = await innkeeper_client.get("/v1/tenants")
    assert resp.status_code == 200, resp.content

    # ASSERT
    resp_content = json.loads(resp.content)
    pp.pprint(resp_content)
    assert len(resp_content) == 1
