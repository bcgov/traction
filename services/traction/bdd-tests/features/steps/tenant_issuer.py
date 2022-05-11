import json, random, string
from pprint import pp
import requests
import time
from behave import *
from starlette import status


@given('"{tenant}" registers as an issuer')
@when('"{tenant}" registers as an issuer')
def step_impl(context, tenant: str):
    response = requests.post(
        context.config.userdata.get("traction_host") + "/tenant/v0/admin/issuer",
        headers=context.config.userdata[tenant]["auth_headers"],
    )
    assert response.status_code == status.HTTP_200_OK, response.__dict__
    resp_json = json.loads(response.content)
    # wait for ensdorser signatures and ledger writes
    time.sleep(2)


@when('"{issuer}" issues "{holder}" a "{schema_name}" credential')
def step_impl(context, issuer: str, holder: str, schema_name: str):

    schema = context.config.userdata["governance"]["schemas"][schema_name]
    # TODO FIX APPLICATION BUG: inviter alias gets overwritten when invitee accepts
    contact_id = context.config.userdata[issuer]["connections"][
        context.config.userdata[holder]["name"]
    ]["contact_id"]

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


## COMPOSED ACTIONS
@given('"{tenant}" is an issuer')
def step_impl(context, tenant):
    context.execute_steps(
        f"""
    Given "{tenant}" is allowed to be an issuer by the innkeeper
    And "{tenant}" registers as an issuer
    """
    )
