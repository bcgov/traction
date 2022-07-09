import json
import requests
import pprint
import time

from behave import *
from starlette import status

from v1_api import *

@step('"{holder}" will have a credential_offer from "{issuer}"')
def step_impl(context, holder: str, issuer: str):
    params = {}
    response = list_holder_credentials(context, holder, params)
    assert response.status_code == status.HTTP_200_OK, response.__dict__
    resp_json = json.loads(response.content)
    assert len(resp_json["items"]) == 1, resp_json

    contact_id = context.config.userdata[holder]["connections"][issuer]["contact_id"]

    assert resp_json["items"][0]["contact"]["contact_id"] == contact_id
    assert resp_json["items"][0]["state"] == "offer_received"

    context.config.userdata[holder]["cred_offers"] = [
        a for a in resp_json["items"]
    ]


@step('"{holder}" will accept credential_offer from "{issuer}"')
def step_impl(context, holder, issuer):
    holder_credential_id = context.config.userdata[holder]["cred_offers"][0]["holder_credential_id"]
    response = accept_holder_credential(context, holder, holder_credential_id)
    assert response.status_code == status.HTTP_200_OK, response.__dict__
    resp_json = json.loads(response.content)
    assert resp_json["item"]["state"] == "request_sent", resp_json
    time.sleep(2)


@step('"{holder}" will have a credential')
def step_impl(context, holder):
    holder_credential_id = context.config.userdata[holder]["cred_offers"][0]["holder_credential_id"]
    response = get_holder_credential(context, holder, holder_credential_id)
    assert response.status_code == status.HTTP_200_OK, response.__dict__
    resp_json = json.loads(response.content)
    assert resp_json["item"]["status"] == "Accepted", resp_json


@step('"{prover}" will have a present-proof request for "{schema_name}"')
def step_impl(context, prover: str, schema_name: str):

    response = requests.get(
        context.config.userdata.get("traction_host")
        + "/tenant/v0/credentials/holder/request",
        headers=context.config.userdata[prover]["auth_headers"],
    )

    assert response.status_code == status.HTTP_200_OK, response.__dict__
    resp_json = json.loads(response.content)
    assert len(resp_json) == 1, resp_json
    assert resp_json[0]["presentation"]["present_role"] == "holder", resp_json[0]

    # update presentation_requests list
    context.config.userdata[prover].setdefault("presentation_requests", resp_json)


@step(
    '"{prover}" will have credentials to satisfy the present-proof request for "{schema_name}"'
)
def step_impl(context, prover: str, schema_name: str):

    response = requests.get(
        context.config.userdata.get("traction_host")
        + "/tenant/v0/credentials/holder/creds-for-request?pres_req_id="
        + context.config.userdata[prover]["presentation_requests"][0]["presentation"][
            "id"
        ],
        headers=context.config.userdata[prover]["auth_headers"],
    )

    assert response.status_code == status.HTTP_200_OK, response.__dict__
    resp_json = json.loads(response.content)
    assert len(resp_json) == 1, resp_json


@step(
    '"{prover}" sends the presentation in response to the request for "{schema_name}"'
)
def step_impl(context, prover: str, schema_name: str):

    pres = context.config.userdata[prover]["presentation_requests"][0]["presentation"]
    cred_id = context.config.userdata[prover]["credentials"][schema_name]["referent"]

    # hard code attr_0,
    body = {
        "requested_attributes": {"attr_0": {"cred_id": cred_id, "revealed": True}},
        "requested_predicates": {},
        "self_attested_attributes": {},
    }

    response = requests.post(
        context.config.userdata.get("traction_host")
        + "/tenant/v0/credentials/holder/present-credential?pres_req_id="
        + pres["id"],
        json=body,
        headers=context.config.userdata[prover]["auth_headers"],
    )
    assert response.status_code == status.HTTP_200_OK, response.__dict__


@step('"{holder}" loads credentials')
def step_impl(context, holder: str):

    response = requests.get(
        context.config.userdata.get("traction_host") + "/tenant/v0/credentials/holder",
        headers=context.config.userdata[holder]["auth_headers"],
    )
    assert response.status_code == status.HTTP_200_OK, response.__dict__
    resp_json = json.loads(response.content)

    creds = {c["schema_id"].split(":")[2]: c for c in resp_json}

    context.config.userdata[holder].setdefault("credentials", creds)
    pprint.pp(context.config.userdata[holder]["credentials"])
