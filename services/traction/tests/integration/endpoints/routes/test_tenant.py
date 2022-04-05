import pytest
import json
from typing import List
import asyncio

from httpx import AsyncClient, ReadTimeout
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
from api.endpoints.models.credentials import CredPrecisForProof

from test_tenant_utils import (
    check_workflow_state,
    create_tenant,
    create_schema_cred_def,
    connect_tenants,
    issue_credential,
    request_credential_presentation,
)


pytestmark = pytest.mark.asyncio


@pytest.mark.integtest
async def test_tenants_connect(app_client: AsyncClient) -> None:
    # get a token
    bearer_token = await innkeeper_auth(app_client)
    ik_headers = innkeeper_headers(bearer_token)

    t1_headers = await create_tenant(
        app_client, ik_headers, tenant_name="tenant1_test_"
    )

    t2_headers = await create_tenant(
        app_client, ik_headers, tenant_name="tenant2_test_"
    )

    t1_connections = await app_client.get("/tenant/v0/connections/", headers=t1_headers)
    assert t1_connections.status_code == 200, t1_connections.content
    assert 0 == len(json.loads(t1_connections.content)), t1_connections.content

    t2_connections = await app_client.get("/tenant/v0/connections/", headers=t2_headers)
    assert t2_connections.status_code == 200, t2_connections.content
    assert 0 == len(json.loads(t2_connections.content)), t2_connections.content

    await connect_tenants(app_client, t1_headers, "alice", t2_headers, "faber")


@pytest.mark.integtest
@pytest.mark.parametrize(
    "support_revocation",
    [
        False,
        True,
    ],
)
async def test_tenant_issuer(support_revocation, app_client: AsyncClient) -> None:
    # get a token
    bearer_token = await innkeeper_auth(app_client)
    ik_headers = innkeeper_headers(bearer_token)

    t1_headers = await create_tenant(
        app_client, ik_headers, tenant_name="tenant1_test_", make_issuer=True
    )

    schema_name = random_string("test_schema_", 8)
    schema = {
        "schema_name": schema_name,
        "schema_version": "1.2.3",
        "attributes": ["score", "full_name", "test_date"],
    }
    cred_def_id = await create_schema_cred_def(
        app_client,
        t1_headers,
        cred_def_tag="test_tag",
        schema=schema,
        revocable=support_revocation,
        revoc_reg_size=10 if support_revocation else None,
    )
    assert cred_def_id, "No cred def id returned"


@pytest.mark.integtest
@pytest.mark.parametrize(
    "support_revocation",
    [
        False,
        True,
    ],
)
async def test_tenants_issue_credential(
    support_revocation, app_client: AsyncClient
) -> None:
    # get a token
    bearer_token = await innkeeper_auth(app_client)
    ik_headers = innkeeper_headers(bearer_token)

    t1_headers = await create_tenant(
        app_client, ik_headers, tenant_name="tenant1_test_", make_issuer=True
    )
    t2_headers = await create_tenant(
        app_client, ik_headers, tenant_name="tenant2_test_"
    )

    schema_name = random_string("test_schema_", 8)
    schema = {
        "schema_name": schema_name,
        "schema_version": "1.2.3",
        "attributes": ["score", "full_name", "test_date"],
    }
    cred_def_id = await create_schema_cred_def(
        app_client,
        t1_headers,
        cred_def_tag="test_tag",
        schema=schema,
        revocable=support_revocation,
        revoc_reg_size=10 if support_revocation else None,
    )
    assert cred_def_id, "No cred def id returned"

    await connect_tenants(app_client, t1_headers, "alice", t2_headers, "faber")

    # should be zero credentials for our t2
    creds_resp = await app_client.get(
        "/tenant/v0/credentials/holder/", headers=t2_headers
    )
    assert creds_resp.status_code == 200, creds_resp.content
    assert 0 == len(json.loads(creds_resp.content)), creds_resp.content

    # now issue a credential from t1 to t2
    credential = {
        "attributes": [
            {"name": "score", "value": "66"},
            {"name": "full_name", "value": "Alice Smith"},
            {"name": "test_date", "value": "April 1, 2022"},
        ]
    }
    await issue_credential(
        app_client,
        t1_headers,
        "alice",
        t2_headers,
        cred_def_id,
        credential,
        check_revoc=support_revocation,
    )

    # should be one credentials for our t2
    creds_resp = await app_client.get(
        "/tenant/v0/credentials/holder/", headers=t2_headers
    )
    assert creds_resp.status_code == 200, creds_resp.content
    assert 1 == len(json.loads(creds_resp.content)), creds_resp.content


@pytest.mark.integtest
@pytest.mark.parametrize(
    "support_revocation",
    [
        False,
        True,
    ],
)
async def test_tenants_issue_credential_request_proof(
    support_revocation, app_client: AsyncClient
) -> None:
    # get a token
    bearer_token = await innkeeper_auth(app_client)
    ik_headers = innkeeper_headers(bearer_token)

    t1_headers = await create_tenant(
        app_client, ik_headers, tenant_name="tenant1_test_", make_issuer=True
    )
    t2_headers = await create_tenant(
        app_client, ik_headers, tenant_name="tenant2_test_"
    )

    schema_name = random_string("test_schema_", 8)
    schema = {
        "schema_name": schema_name,
        "schema_version": "4.5.6",
        "attributes": ["score", "full_name", "test_date"],
    }
    cred_def_id = await create_schema_cred_def(
        app_client,
        t1_headers,
        cred_def_tag="test_tag",
        schema=schema,
        revocable=support_revocation,
        revoc_reg_size=10 if support_revocation else None,
    )
    assert cred_def_id, "No cred def id returned"

    await connect_tenants(app_client, t1_headers, "alice", t2_headers, "faber")

    # should be zero credentials for our t2
    creds_resp = await app_client.get(
        "/tenant/v0/credentials/holder/", headers=t2_headers
    )
    assert creds_resp.status_code == 200, creds_resp.content
    assert 0 == len(json.loads(creds_resp.content)), creds_resp.content

    # now issue a credential from t1 to t2
    credential = {
        "attributes": [
            {"name": "score", "value": "66"},
            {"name": "full_name", "value": "Alice Smith"},
            {"name": "test_date", "value": "April 1, 2022"},
        ]
    }
    await issue_credential(
        app_client,
        t1_headers,
        "alice",
        t2_headers,
        cred_def_id,
        credential,
        check_revoc=support_revocation,
    )

    # should be one credentials for our t2
    creds_resp = await app_client.get(
        "/tenant/v0/credentials/holder/", headers=t2_headers
    )
    assert creds_resp.status_code == 200, creds_resp.content
    assert 1 == len(json.loads(creds_resp.content)), creds_resp.content

    # now request a proof t1 to t2
    proof_req = {
        "requested_attributes": [
            {
                "name": "full_name",
                "restrictions": [{"cred_def_id": cred_def_id}],
            }
        ],
        "requested_predicates": [
            {
                "name": "score",
                "p_type": ">",
                "p_value": 50,
                "restrictions": [{"cred_def_id": cred_def_id}],
            }
        ],
    }
    await request_credential_presentation(
        app_client, t1_headers, "alice", t2_headers, proof_req
    )
