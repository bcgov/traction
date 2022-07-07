import pytest
import json
from typing import List
import asyncio
import time

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
    revoke_credential,
)


pytestmark = pytest.mark.asyncio


# @pytest.mark.integtest
@pytest.mark.parametrize(
    "prove_non_revocation",
    [
        False,
        True,
    ],
)
async def x_test_tenants_issue_cred_req_proof_revoke(
    prove_non_revocation, app_client: AsyncClient
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
        revocable=True,
        revoc_reg_size=10,
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
    (issuer_workflow_id, holder_workflow_id) = await issue_credential(
        app_client,
        t1_headers,
        "alice",
        t2_headers,
        cred_def_id,
        credential,
        check_revoc=True,
    )

    # should be one credentials for our t2
    creds_resp = await app_client.get(
        "/tenant/v0/credentials/holder/", headers=t2_headers
    )
    assert creds_resp.status_code == 200, creds_resp.content
    held_credentials = json.loads(creds_resp.content)
    assert 1 == len(held_credentials), creds_resp.content

    # let's get the rev_reg_id and cred_rev_id from the credential
    held_cred = held_credentials[0]
    held_rev_reg_id = held_cred["rev_reg_id"]
    held_cred_rev_id = held_cred["cred_rev_id"]

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
    if prove_non_revocation:
        # pause to ensure we get a clean non-revoc interval
        await asyncio.sleep(2)
        revoc = {"to": int(time.time())}
        proof_req["requested_attributes"][0]["non_revoked"] = revoc
        proof_req["requested_predicates"][0]["non_revoked"] = revoc
        proof_req["non_revoked"] = revoc
    await request_credential_presentation(
        app_client,
        t1_headers,
        "alice",
        t2_headers,
        proof_req,
        will_validate=True,
    )

    await asyncio.sleep(2)

    # now revoke the credential
    await revoke_credential(
        app_client,
        t1_headers,
        t2_headers,
        rev_reg_id=held_rev_reg_id,
        cred_rev_id=held_cred_rev_id,
        issuer_workflow_id=issuer_workflow_id,
        holder_workflow_id=holder_workflow_id,
    )

    if prove_non_revocation:
        # pause to ensure we get a clean non-revoc interval
        await asyncio.sleep(5)
        revoc = {"to": int(time.time())}
        proof_req["requested_attributes"][0]["non_revoked"] = revoc
        proof_req["requested_predicates"][0]["non_revoked"] = revoc
        proof_req["non_revoked"] = revoc

    # proof should still be valid (unless we're checking non-revocation)
    await request_credential_presentation(
        app_client,
        t1_headers,
        "alice",
        t2_headers,
        proof_req,
        will_validate=(not prove_non_revocation),
    )
