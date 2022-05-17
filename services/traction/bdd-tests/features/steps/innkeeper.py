import json
import requests
from behave import *
from starlette import status


@given('"{tenant}" is allowed to be an issuer by the innkeeper')
@when('"{tenant}" is allowed to be an issuer by the innkeeper')
def step_impl(context, tenant: str):
    response = requests.post(
        context.config.userdata.get("traction_host")
        + "/innkeeper/v0/issuers/"
        + context.config.userdata[tenant]["tenant_id"],
        headers=context.config.userdata["innkeeper_auth_headers"],
    )
    assert response.status_code == status.HTTP_200_OK, response.__dict__


@then('"{tenant}" will have a public did')
@given('"{tenant}" will have a public did')
def step_impl(context, tenant: str):
    response = requests.get(
        context.config.userdata.get("traction_host")
        + "/innkeeper/v0/issuers/"
        + context.config.userdata[tenant]["tenant_id"],
        headers=context.config.userdata["innkeeper_auth_headers"],
    )
    assert response.status_code == status.HTTP_200_OK, response.__dict__
    resp_json = json.loads(response.content)
    assert "public_did" in resp_json.keys(), resp_json
    assert resp_json["public_did"] is not None, resp_json
