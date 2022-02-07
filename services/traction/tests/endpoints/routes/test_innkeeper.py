import pytest
import json
import pprint
from tests.db.tenant_factory import CheckInRequestFactory
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.testclient import TestClient


pp = pprint.PrettyPrinter()


@pytest.mark.asyncio
async def test_tenants_get_all(innkeeper_client: TestClient) -> None:
    # ARRANGE
    create_checkin_body = CheckInRequestFactory.build()
    resp = innkeeper_client.post("/v1/check-in", json=create_checkin_body.dict())
    assert resp.ok, resp.__dict__

    # ACT
    resp = innkeeper_client.get("/v1/tenants")
    assert resp.ok

    # ASSERT
    resp_content = json.loads(resp.content)
    pp.pprint(resp_content)
    assert len(resp_content) == 1
