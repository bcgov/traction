import pytest
import json
import time

from httpx import AsyncClient
from pydantic import parse_obj_as

from tests.test_utils import (
    random_string,
    innkeeper_auth,
    innkeeper_headers,
    tenant_auth,
    tenant_headers,
)

from api.db.models.tenant import TenantRead
from api.db.models.tenant_issuer import TenantIssuerRead
from api.endpoints.models.innkeeper import CheckInResponse


pytestmark = pytest.mark.asyncio


@pytest.mark.integtest
async def test_tenants_connect(test_client: AsyncClient) -> None:
    # get a token
    bearer_token = await innkeeper_auth(test_client)
    ik_headers = innkeeper_headers(bearer_token)

    # ARRANGE
    tenant1_name = random_string("tenant1_test_", 12)
    data = {"name": tenant1_name}
    resp_tenant1 = await test_client.post(
        "/innkeeper/v1/check-in", json=data, headers=ik_headers
    )
    assert resp_tenant1.status_code == 201, resp_tenant1.content
    c1_resp = CheckInResponse(**resp_tenant1.json())

    t1_token = await tenant_auth(test_client, c1_resp.wallet_id, c1_resp.wallet_key)
    t1_headers = tenant_headers(t1_token)

    tenant2_name = random_string("tenant2_test_", 12)
    data = {"name": tenant2_name}
    resp_tenant2 = await test_client.post(
        "/innkeeper/v1/check-in", json=data, headers=ik_headers
    )
    assert resp_tenant2.status_code == 201, resp_tenant2.content
    c2_resp = CheckInResponse(**resp_tenant2.json())

    t2_token = await tenant_auth(test_client, c2_resp.wallet_id, c2_resp.wallet_key)
    t2_headers = tenant_headers(t2_token)

    t1_connections = await test_client.get("/tenant/v1/connections/", headers=t1_headers)
    assert t1_connections.status_code == 200, t1_connections.content
    assert 0 == len(json.loads(t1_connections.content)), t1_connections.content

    t2_connections = await test_client.get("/tenant/v1/connections/", headers=t2_headers)
    assert t2_connections.status_code == 200, t2_connections.content
    assert 0 == len(json.loads(t2_connections.content)), t2_connections.content

    data = {"alias": "alice", "invitation_type": "didexchange/1.0"}
    resp_invitation = await test_client.post("/tenant/v1/connections/create-invitation", params=data, headers=t1_headers)
    assert resp_invitation.status_code == 200, resp_invitation.content

    invitation = json.loads(resp_invitation.content)

    data = {"alias": "faber"}
    resp_connection = await test_client.post("/tenant/v1/connections/receive-invitation", params=data, json=invitation["invitation"], headers=t2_headers)
    assert resp_connection.status_code == 200, resp_connection.content

    i = 5
    completed = False
    while 0 < i and not completed:
        t1_connections_resp = await test_client.get("/tenant/v1/connections/", headers=t1_headers)
        assert t1_connections_resp.status_code == 200, t1_connections_resp.content
        t1_connections = json.loads(t1_connections_resp.content)
        assert 1 == len(t1_connections), t1_connections

        t2_connections_resp = await test_client.get("/tenant/v1/connections/", headers=t2_headers)
        assert t2_connections_resp.status_code == 200, t2_connections_resp.content
        t2_connections = json.loads(t2_connections_resp.content)
        assert 1 == len(t2_connections), t2_connections

        completed = (t1_connections[0]["state"] == "active" and t2_connections[0]["state"] == "active")
        if not completed:
            time.sleep(2)
        i -= 1

    assert completed, t1_connections[0]["state"] + ":" + t2_connections[0]["state"]


@pytest.mark.integtest
async def test_tenant_issuer(test_client: AsyncClient) -> None:
    # get a token
    bearer_token = await innkeeper_auth(test_client)
    ik_headers = innkeeper_headers(bearer_token)

    # ARRANGE
    tenant1_name = random_string("tenant1_test_", 12)
    data = {"name": tenant1_name}
    resp_tenant1 = await test_client.post(
        "/innkeeper/v1/check-in", json=data, headers=ik_headers
    )
    assert resp_tenant1.status_code == 201, resp_tenant1.content
    c1_resp = CheckInResponse(**resp_tenant1.json())

    t1_token = await tenant_auth(test_client, c1_resp.wallet_id, c1_resp.wallet_key)
    t1_headers = tenant_headers(t1_token)

    resp_issuer1 = await test_client.post(f"/innkeeper/v1/issuers/{c1_resp.id}", headers=ik_headers)
    assert resp_issuer1.status_code == 200, resp_issuer1.content

    resp_issuer1 = await test_client.post("/tenant/v1/admin/issuer", headers=t1_headers)
    assert resp_issuer1.status_code == 200, resp_issuer1.content

    i = 5
    completed = False
    while i > 0 and not completed:
        # wait for the issuer process to complete
        resp_issuer1 = await test_client.get("/tenant/v1/admin/issuer", headers=t1_headers)
        assert resp_issuer1.status_code == 200, resp_issuer1.content

        issuer = json.loads(resp_issuer1.content)
        completed = (issuer["workflow"]["workflow_state"] == "complete")
        if not completed:
            time.sleep(2)
        i -= 1

    assert completed, issuer["workflow"]["workflow_state"]
