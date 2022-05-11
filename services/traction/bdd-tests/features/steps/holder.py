import json
import requests

from behave import *
from starlette import status


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
