import json
import requests
import pprint
import time

from behave import *
from starlette import status


@when('"{holder}" will have a credential_offer from "{issuer}"')
@then('"{holder}" will have a credential_offer from "{issuer}"')
def step_impl(context, holder: str, issuer: str):
    response = requests.get(
        context.config.userdata.get("traction_host")
        + "/tenant/v0/credentials/holder/offer",
        headers=context.config.userdata[holder]["auth_headers"],
    )
    assert response.status_code == status.HTTP_200_OK, response.__dict__
    resp_json = json.loads(response.content)
    assert len(resp_json) == 1, resp_json

    # TODO FIX APPLICATION BUG: inviter alias gets overwritten when invitee accepts
    contact_id = context.config.userdata[holder]["connections"][issuer]["contact_id"]

    assert resp_json[0]["credential"]["contact_id"] == contact_id
    assert resp_json[0]["credential"]["issue_state"] == "offer_received"

    context.config.userdata[holder]["cred_offers"] = [
        a["credential"] for a in resp_json
    ]


@when('"{holder}" will accept credential_offer from "{issuer}"')
@then('"{holder}" will accept credential_offer from "{issuer}"')
def step_impl(context, holder, issuer):

    cred_issue_id = context.config.userdata[holder]["cred_offers"][0]["id"]

    response = requests.post(
        context.config.userdata.get("traction_host")
        + "/tenant/v0/credentials/holder/accept_offer"
        + "?cred_issue_id="
        + cred_issue_id,
        headers=context.config.userdata[holder]["auth_headers"],
    )

    assert response.status_code == status.HTTP_200_OK, response.__dict__
    resp_json = json.loads(response.content)
    assert resp_json["credential"]["issue_state"] == "request_sent", resp_json
    time.sleep(2)


@then('"{holder}" will have a credential')
def step_impl(context, holder):

    response = requests.get(
        context.config.userdata.get("traction_host") + "/tenant/v0/credentials/holder/",
        headers=context.config.userdata[holder]["auth_headers"],
    )

    assert response.status_code == status.HTTP_200_OK, response.__dict__
    resp_json = json.loads(response.content)
    assert len(resp_json) == 1, resp_json
