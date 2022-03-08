import pytest
import json

from httpx import AsyncClient

from tests.test_utils import random_string, innkeeper_auth, innkeeper_headers


pytestmark = pytest.mark.asyncio


@pytest.mark.integtest
async def test_tenants_get_all(
    test_client: AsyncClient
) -> None:
    # get a token
    bearer_token = await innkeeper_auth(test_client)
    headers = innkeeper_headers(bearer_token)

    # ARRANGE
    resp = await test_client.get("/innkeeper/v1/tenants", headers=headers)
    assert resp.status_code == 200, resp.content
    resp_content = json.loads(resp.content)
    existing_len = len(resp_content)

    tenant_name = random_string("tenant_test_", 12)
    data = {"name": tenant_name}
    resp_tenant = await test_client.post("/innkeeper/v1/check-in", json=data, headers=headers)
    assert resp_tenant.status_code == 201, resp_tenant.content

    # ACT
    resp = await test_client.get("/innkeeper/v1/tenants", headers=headers)
    assert resp.status_code == 200, resp.content

    # ASSERT
    resp_content = json.loads(resp.content)
    assert (len(resp_content)-existing_len) == 1, len(resp_content)
