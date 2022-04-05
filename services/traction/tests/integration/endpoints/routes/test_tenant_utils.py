import json
from typing import List
import asyncio
import os

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
from api.endpoints.models.credentials import (
    CredPrecisForProof,
    CredentialStateType,
)


default_retry_attempts = int(os.environ.get("DEFAULT_RETRY_ATTEMPTS", "11"))
default_pause_between_attempts = int(
    os.environ.get("DEFAULT_PAUSE_BETWEEN_ATTEMPTS", "2")
)


async def check_workflow_state(
    app_client: AsyncClient,
    t1_headers: dict,
    workflow_url: str,
    workflow_id: str = None,
    expected_state: str = "completed",
    attempts: int = default_retry_attempts,
    delay: int = default_pause_between_attempts,
):
    """Check (wait) for the workflow to finish with the given state."""

    i = attempts
    completed = False
    workflow = None
    while i > 0 and not completed:
        try:
            # wait for the issuer process to complete
            resp_workflows1 = await app_client.get(workflow_url, headers=t1_headers)
            assert resp_workflows1.status_code == 200, resp_workflows1.content

            workflows = json.loads(resp_workflows1.content)
            workflow = None
            if workflow_id:
                # assume a list
                for wf in workflows:
                    if wf.get("workflow") and wf["workflow"]["id"] == workflow_id:
                        workflow = wf
                        break
            else:
                # assume there is just one
                workflow = workflows
            assert workflow, f"Workflow not found for {workflow_id}"
            completed = workflow["workflow"]["workflow_state"] == expected_state
        except ReadTimeout:
            # ignore and retry
            pass

        if not completed:
            await asyncio.sleep(delay)
        i -= 1

    assert completed, workflow["workflow"]["workflow_state"]

    return workflow


async def create_tenant(
    app_client: AsyncClient,
    ik_headers: dict,
    tenant_name: str = "tenant_test_",
    make_issuer: bool = False,
) -> dict:
    """Create a new tenant and optionally set as issuer."""

    tenant1_name = random_string(tenant_name, 12)
    data = {"name": tenant1_name}
    resp_tenant1 = await app_client.post(
        "/innkeeper/v0/check-in", json=data, headers=ik_headers
    )
    assert resp_tenant1.status_code == 201, resp_tenant1.content
    c1_resp = CheckInResponse(**resp_tenant1.json())

    t1_token = await tenant_auth(app_client, c1_resp.wallet_id, c1_resp.wallet_key)
    t1_headers = tenant_headers(t1_token)

    if not make_issuer:
        return t1_headers

    resp_issuer1 = await app_client.post(
        f"/innkeeper/v0/issuers/{c1_resp.id}", headers=ik_headers
    )
    assert resp_issuer1.status_code == 200, resp_issuer1.content

    resp_issuer1 = await app_client.post("/tenant/v0/admin/issuer", headers=t1_headers)
    assert resp_issuer1.status_code == 200, resp_issuer1.content

    await check_workflow_state(app_client, t1_headers, "/tenant/v0/admin/issuer")

    return t1_headers


async def create_schema_cred_def(
    app_client: AsyncClient,
    t1_headers: dict,
    schema_id: str = None,
    cred_def_tag: str = None,
    schema: dict = None,
    revocable: bool = False,
    revoc_reg_size: int = 10,
) -> str:
    """Create a schema and/or credential definition for the given issuer tenant."""

    # make sure our tenant is actually an issuer
    resp_issuer1 = await app_client.get("/tenant/v0/admin/issuer", headers=t1_headers)
    assert resp_issuer1.status_code == 200, resp_issuer1.content
    issuer = json.loads(resp_issuer1.content)
    assert issuer.get("workflow")
    assert issuer["workflow"]["workflow_state"] == "completed"

    params = {"schema_id": schema_id, "cred_def_tag": cred_def_tag}
    if revocable:
        params["revocable"] = revocable
        params["revoc_reg_size"] = revoc_reg_size
    schema_resp = await app_client.post(
        "/tenant/v0/admin/schema", headers=t1_headers, params=params, json=schema
    )
    assert schema_resp.status_code == 200, schema_resp.content
    schema = json.loads(schema_resp.content)
    workflow_id = schema["workflow"]["id"]

    # pause here, seems to be a timing issue creating cred defs
    await asyncio.sleep(default_pause_between_attempts)

    await check_workflow_state(
        app_client, t1_headers, "/tenant/v0/admin/schema", workflow_id=workflow_id
    )

    schema_resp = await app_client.get("/tenant/v0/admin/schema", headers=t1_headers)
    assert schema_resp.status_code == 200, schema_resp.content

    schemas = json.loads(schema_resp.content)
    for schema in schemas:
        if schema.get("workflow") and schema["workflow"]["id"] == workflow_id:
            return schema["schema_data"]["cred_def_id"]

    assert False, f"Error no schema found for workflow {workflow_id}"


async def connect_tenants(
    app_client: AsyncClient,
    t1_headers: dict,
    t1_alias: str,
    t2_headers: dict,
    t2_alias: str,
    invitation_type: str = "didexchange/1.0",
):
    """Establish a connection between the two given tenants."""

    data = {"alias": t1_alias, "invitation_type": invitation_type}
    resp_invitation = await app_client.post(
        "/tenant/v0/connections/create-invitation", params=data, headers=t1_headers
    )
    assert resp_invitation.status_code == 200, resp_invitation.content

    invitation = json.loads(resp_invitation.content)

    data = {"alias": t2_alias}
    resp_connection = await app_client.post(
        "/tenant/v0/connections/receive-invitation",
        params=data,
        json=json.loads(invitation["connection"]["invitation"]),
        headers=t2_headers,
    )
    assert resp_connection.status_code == 200, resp_connection.content

    i = default_retry_attempts
    completed = False
    while 0 < i and not completed:
        t1_connections_resp = await app_client.get(
            "/tenant/v0/connections/", headers=t1_headers, params={"alias": t1_alias}
        )
        assert t1_connections_resp.status_code == 200, t1_connections_resp.content
        t1_connections = json.loads(t1_connections_resp.content)
        assert 1 == len(t1_connections), t1_connections

        t2_connections_resp = await app_client.get(
            "/tenant/v0/connections/", headers=t2_headers, params={"alias": t2_alias}
        )
        assert t2_connections_resp.status_code == 200, t2_connections_resp.content
        t2_connections = json.loads(t2_connections_resp.content)
        assert 1 == len(t2_connections), t2_connections

        completed = (
            t1_connections[0]["state"] == "active"
            and t2_connections[0]["state"] == "active"
        )
        if not completed:
            await asyncio.sleep(default_pause_between_attempts)
        i -= 1

    assert completed, t1_connections[0]["state"] + ":" + t2_connections[0]["state"]


async def issue_credential(
    app_client: AsyncClient,
    t1_headers: dict,
    t1_alias: str,
    t2_headers: dict,
    cred_def_id: str,
    credential: dict,
    cred_protocol: str = "v1.0",
    accept_offer: bool = True,
    check_revoc: bool = False,
) -> (str, str):
    """Issue a credential from issuer (t1) to holder (t2)."""

    params = {
        "cred_protocol": cred_protocol,
        "cred_def_id": cred_def_id,
        "alias": t1_alias,
    }
    issue_resp = await app_client.post(
        "/tenant/v0/credentials/issuer/issue",
        headers=t1_headers,
        params=params,
        json=credential,
    )
    assert issue_resp.status_code == 200, issue_resp.content
    issue_data = json.loads(issue_resp.content)
    assert issue_data.get("workflow"), "Error no workflow returned"
    issue_workflow_id = issue_data["workflow"]["id"]

    holder_data = None
    i = default_retry_attempts
    while i > 0 and not holder_data:
        holder_resp = await app_client.get(
            "/tenant/v0/credentials/holder/offer",
            headers=t2_headers,
            params={"state": "pending"},
        )
        assert holder_resp.status_code == 200, holder_resp.content
        if 0 < len(json.loads(holder_resp.content)):
            holder_data = json.loads(holder_resp.content)[0]
        else:
            await asyncio.sleep(default_pause_between_attempts)
            i -= 1
    assert holder_data, "Error no cred offer received by holder"

    # for exception scenarios, let the caller handle things ...
    if not accept_offer:
        return issue_workflow_id, holder_data["credential"]["id"]

    holder_resp = await app_client.post(
        "/tenant/v0/credentials/holder/accept_offer",
        headers=t2_headers,
        params={"cred_issue_id": holder_data["credential"]["id"]},
    )
    assert holder_resp.status_code == 200, holder_resp.content
    holder_data = json.loads(holder_resp.content)
    assert holder_data.get("workflow"), "Error no workflow returned"
    holder_workflow_id = holder_data["workflow"]["id"]

    issue_rec = await check_workflow_state(
        app_client,
        t1_headers,
        "/tenant/v0/credentials/issuer/issue",
        workflow_id=issue_workflow_id,
    )

    if check_revoc:
        cred = issue_rec["credential"]
        assert cred.get("rev_reg_id") is not None, "Error no revocation info"
        assert cred.get("cred_rev_id") is not None, "Error no revocation info"

    await check_workflow_state(
        app_client,
        t2_headers,
        "/tenant/v0/credentials/holder/offer",
        workflow_id=holder_workflow_id,
    )

    # workflows completed there should be a new credential available
    creds_resp = await app_client.get(
        "/tenant/v0/credentials/holder/", headers=t2_headers
    )
    assert creds_resp.status_code == 200, creds_resp.content
    assert 1 == len(json.loads(creds_resp.content)), creds_resp.content

    return issue_workflow_id, holder_workflow_id


async def request_credential_presentation(
    app_client: AsyncClient,
    t1_headers: dict,
    t1_alias: str,
    t2_headers: dict,
    proof_req: dict,
    pres_protocol: str = "v1.0",
    accept_request: bool = True,
    will_validate: bool = True,
) -> (str, str):
    """Request a presentation from t1 (verifier) to t2 (holder)."""

    params = {
        "pres_protocol": pres_protocol,
        "alias": t1_alias,
    }
    pres_resp = await app_client.post(
        "/tenant/v0/credentials/verifier/request",
        headers=t1_headers,
        params=params,
        json=proof_req,
    )
    assert pres_resp.status_code == 200, pres_resp.content
    pres_data = json.loads(pres_resp.content)
    assert pres_data.get("workflow"), "Error no workflow returned"
    pres_req_workflow_id = pres_data["workflow"]["id"]

    holder_data = None
    i = default_retry_attempts
    while i > 0 and not holder_data:
        holder_resp = await app_client.get(
            "/tenant/v0/credentials/holder/request",
            headers=t2_headers,
            params={"state": "pending"},
        )
        assert holder_resp.status_code == 200, holder_resp.content
        if 0 < len(json.loads(holder_resp.content)):
            holder_data = json.loads(holder_resp.content)[0]
        else:
            await asyncio.sleep(default_pause_between_attempts)
            i -= 1
    assert holder_data, "Error no pres request received by holder"
    present_request = json.loads(holder_data["presentation"]["present_request"])

    if not accept_request:
        return pres_req_workflow_id, holder_data["presentation"]["id"]

    holder_resp = await app_client.get(
        "/tenant/v0/credentials/holder/creds-for-request",
        headers=t2_headers,
        params={"pres_req_id": holder_data["presentation"]["id"]},
    )
    assert holder_resp.status_code == 200, holder_resp.content
    cred_results = parse_obj_as(List[CredPrecisForProof], holder_resp.json())

    proof_presentation = build_proof_presentation(present_request, cred_results)

    # submit proof
    holder_resp = await app_client.post(
        "/tenant/v0/credentials/holder/present-credential",
        headers=t2_headers,
        params={"pres_req_id": holder_data["presentation"]["id"]},
        json=proof_presentation,
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
    )
    await check_workflow_state(
        app_client,
        t2_headers,
        "/tenant/v0/credentials/holder/request",
        workflow_id=holder_workflow_id,
    )

    # get the verifier-received proof and validate
    params = {"workflow_id": pres_req_workflow_id}
    recd_pres = await app_client.get(
        "/tenant/v0/credentials/verifier/request",
        headers=t1_headers,
        params=params,
    )
    assert recd_pres.status_code == 200, recd_pres.content
    pres_data = json.loads(recd_pres.content)
    assert 1 == len(pres_data)
    presentation = json.loads(pres_data[0]["presentation"]["presentation"])
    verified = "true" if will_validate else "false"
    assert verified == presentation["verified"], recd_pres.content

    return pres_req_workflow_id, holder_workflow_id


def build_proof_presentation(
    present_request: dict,
    cred_results: List[CredPrecisForProof],
) -> dict:
    proof_presentation = {
        "requested_attributes": {},
        "requested_predicates": {},
        "self_attested_attributes": {},
    }
    for attr_name in present_request["requested_attributes"]:
        for cred in cred_results:
            if attr_name in cred.presentation_referents:
                proof_presentation["requested_attributes"][attr_name] = {
                    "cred_id": cred.cred_info["referent"],
                    "revealed": True,
                }
                break
        if attr_name not in proof_presentation["requested_attributes"]:
            proof_presentation["self_attested_attributes"][
                attr_name
            ] = "TBD Self-attested"
    for pred_name in present_request["requested_predicates"]:
        for cred in cred_results:
            if pred_name in cred.presentation_referents:
                proof_presentation["requested_predicates"][pred_name] = {
                    "cred_id": cred.cred_info["referent"],
                }
                break

    return proof_presentation


async def revoke_credential(
    app_client: AsyncClient,
    t1_headers: dict,
    t2_headers: dict,
    cred_issue_id: str = None,
    rev_reg_id: str = None,
    cred_rev_id: str = None,
    verify_revoc: bool = True,
    issuer_workflow_id: str = None,
    holder_workflow_id: str = None,
):
    params = {}
    if cred_issue_id:
        params = {
            "cred_issue_id": cred_issue_id,
        }
    else:
        params = {
            "rev_reg_id": rev_reg_id,
            "cred_rev_id": cred_rev_id,
        }
    revoc_resp = await app_client.post(
        "/tenant/v0/credentials/issuer/revoke",
        headers=t1_headers,
        params=params,
    )
    assert revoc_resp.status_code == 200, revoc_resp.content

    # check the issuer and holder credential status
    if verify_revoc and issuer_workflow_id:
        issue_data = {"credential": {"issue_state": "n/a"}}
        i = default_retry_attempts
        while i > 0 and (
            not issue_data["credential"]["issue_state"]
            == CredentialStateType.credential_revoked
        ):
            await asyncio.sleep(default_pause_between_attempts)
            params = {"workflow_id": issuer_workflow_id}
            issue_resp = await app_client.get(
                "/tenant/v0/credentials/issuer/issue",
                headers=t1_headers,
                params=params,
            )
            assert issue_resp.status_code == 200, issue_resp.content
            issue_datas = json.loads(issue_resp.content)
            assert 1 == len(issue_datas), issue_resp.content
            issue_data = issue_datas[0]
            i -= 1
        assert (
            issue_data["credential"]["issue_state"]
            == CredentialStateType.credential_revoked
        ), issue_data["credential"]["issue_state"]

    if verify_revoc and holder_workflow_id:
        offer_data = {"credential": {"issue_state": "n/a"}}
        i = default_retry_attempts
        while i > 0 and (
            not offer_data["credential"]["issue_state"]
            == CredentialStateType.credential_revoked
        ):
            await asyncio.sleep(default_pause_between_attempts)
            params = {"workflow_id": holder_workflow_id}
            offer_resp = await app_client.get(
                "/tenant/v0/credentials/holder/offer",
                headers=t2_headers,
                params=params,
            )
            assert offer_resp.status_code == 200, offer_resp.content
            offer_datas = json.loads(offer_resp.content)
            assert 1 == len(offer_datas), offer_resp.content
            offer_data = offer_datas[0]
            i -= 1
        assert (
            offer_data["credential"]["issue_state"]
            == CredentialStateType.credential_revoked
        ), offer_data["credential"]["issue_state"]
