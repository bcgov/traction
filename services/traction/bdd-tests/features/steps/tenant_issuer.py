import json, random, string
import uuid
from pprint import pp
import requests
import time
from behave import *
from starlette import status


@given('"{tenant}" registers as an issuer')
@when('"{tenant}" registers as an issuer')
def step_impl(context, tenant: str):
    response = requests.post(
        context.config.userdata.get("traction_host") + "/tenant/v1/admin/make-issuer",
        headers=context.config.userdata[tenant]["auth_headers"],
    )
    assert response.status_code == status.HTTP_200_OK, response.__dict__
    resp_json = json.loads(response.content)
    # wait for endorser signatures and ledger writes
    time.sleep(2)


@when('"{issuer}" issues "{holder}" a "{schema_name}" credential')
def step_impl(context, issuer: str, holder: str, schema_name: str):

    schema = context.config.userdata["governance"]["schemas"][schema_name]
    contact_id = context.config.userdata[issuer]["connections"][holder]["contact_id"]

    data = {
        "cred_protocol": "v1.0",
        "credential": {
            "attributes": [
                {
                    "name": attr_name,
                    "value": "".join(random.choice(string.ascii_letters)),
                }
                for attr_name in json.loads(schema["schema_attrs"])
            ]
        },
        "cred_def_id": schema["cred_def_id"],
        "contact_id": contact_id,
    }

    response = requests.post(
        context.config.userdata.get("traction_host") + "/tenant/v1/issuer/credentials",
        headers=context.config.userdata[issuer]["auth_headers"],
        json=data,
    )
    assert response.status_code == status.HTTP_201_CREATED, response.__dict__


@then('"{issuer}" will have an acked credential_offer')
def step_impl(context, issuer):
    response = requests.get(
        context.config.userdata.get("traction_host")
        + "/tenant/v1/issuer/credentials"
        + "?state=completed",
        headers=context.config.userdata[issuer]["auth_headers"],
    )
    assert response.status_code == status.HTTP_200_OK, response.status
    resp_json = json.loads(response.content)
    assert len(resp_json["items"]) == 1, resp_json


## COMPOSED ACTIONS
@given('"{tenant}" is an issuer')
def step_impl(context, tenant):
    context.execute_steps(
        f"""
    Given "{tenant}" is allowed to be an issuer by the innkeeper
    And "{tenant}" registers as an issuer
    And we sadly wait for {3} seconds because we have not figured out how to listen for events
    And "{tenant}" will have a public did   
    """
    )
