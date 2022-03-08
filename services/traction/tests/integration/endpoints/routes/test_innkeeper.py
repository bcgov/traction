import pytest
import json
import string
import random

from tests.integration.db.tenant_factory import TenantCreateFactory
from api.db.repositories.tenants import TenantsRepository
from sqlalchemy.ext.asyncio import AsyncSession

from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


def random_string(prefix: str, length: int = 10) -> str:
    letters = string.ascii_lowercase
    return prefix.join(random.choice(letters) for i in range(length))


@pytest.mark.integtest
async def test_tenants_get_all(
    test_client: AsyncClient, db_session: AsyncSession
) -> None:
    # get a token
    data = {"username":"innkeeper", "password":"change-me"}
    token_resp = await test_client.post("/innkeeper/token", data=data)
    assert token_resp.status_code == 200, token_resp.content
    token_content = json.loads(token_resp.content)
    bearer_token = "Bearer " + token_content["access_token"]
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": bearer_token,
    }

    # ARRANGE
    resp = await test_client.get("/innkeeper/v1/tenants", headers=headers)
    assert resp.status_code == 200, resp.content
    resp_content = json.loads(resp.content)
    existing_len = len(resp_content)

    #_repo = TenantsRepository(db_session=db_session)
    #test_tenant = TenantCreateFactory.build()
    #await _repo.create(test_tenant)
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
