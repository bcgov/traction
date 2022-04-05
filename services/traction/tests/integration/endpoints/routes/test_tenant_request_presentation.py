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
async def test_tenants_issue_cred_request_proof_reject_request(
    app_client: AsyncClient,
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
        app_client, t1_headers, "alice", t2_headers, cred_def_id, credential
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
    (pres_req_workflow_id, holder_present_id) = await request_credential_presentation(
        app_client, t1_headers, "alice", t2_headers, proof_req, accept_request=False
    )

    # reject proof request
    holder_resp = await app_client.post(
        "/tenant/v0/credentials/holder/reject-request",
        headers=t2_headers,
        params={"pres_req_id": holder_present_id},
    )
    assert holder_resp.status_code == 200, holder_resp.content
    holder_data = json.loads(holder_resp.content)
    assert holder_data.get("workflow"), "Error no workflow returned"
    holder_workflow_id = holder_data["workflow"]["id"]

    await check_workflow_state(
        app_client,
        t1_headers,
        "/tenant/v0/credentials/verifier/request",
        workflow_id=pres_req_workflow_id,
        expected_state="error",
    )
    await check_workflow_state(
        app_client,
        t2_headers,
        "/tenant/v0/credentials/holder/request",
        workflow_id=holder_workflow_id,
        expected_state="error",
    )
