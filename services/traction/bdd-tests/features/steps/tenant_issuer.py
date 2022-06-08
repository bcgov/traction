import json, random, string
from behave import *
from starlette import status
from v1_api import *


@step('"{tenant}" is not an issuer')
def step_impl(context, tenant: str):
    response = get_tenant_self(context, tenant)
    assert response.status_code == status.HTTP_200_OK, response.__dict__
    resp_json = json.loads(response.content)
    assert not resp_json["item"]["issuer"]
    assert resp_json["item"]["issuer_status"] == "N/A"


@step('"{tenant}" is an issuer')
def step_impl(context, tenant: str):
    response = get_tenant_self(context, tenant)
    assert response.status_code == status.HTTP_200_OK, response.__dict__
    resp_json = json.loads(response.content)
    assert resp_json["item"]["issuer"]
    assert resp_json["item"]["issuer_status"] == "Active"


@step('"{tenant}" cannot register as an issuer')
def step_impl(context, tenant: str):
    response = tenant_make_issuer(context, tenant)
    assert response.status_code == status.HTTP_409_CONFLICT, response.__dict__


@step('"{tenant}" registers as an issuer')
def step_impl(context, tenant: str):
    response = tenant_make_issuer(context, tenant)
    assert response.status_code == status.HTTP_200_OK, response.__dict__


@when('"{issuer}" issues "{holder}" a "{schema_name}" credential')
def step_impl(context, issuer: str, holder: str, schema_name: str):

    schema_template = context.config.userdata[issuer][schema_name]["schema_template"]
    credential_template = context.config.userdata[issuer][schema_name][
        "credential_template"
    ]
    contact_id = context.config.userdata[issuer]["connections"][holder]["contact_id"]

    schema_attrs = schema_template["attributes"]
    credential_template_id = credential_template["credential_template_id"]
    data = {
        "contact_id": contact_id,
        "credential_template_id": credential_template_id,
        "attributes": [
            {
                "name": attr_name,
                "value": "".join(random.choice(string.ascii_letters)),
            }
            for attr_name in schema_attrs
        ],
    }

    response = requests.post(
        context.config.userdata.get("traction_host") + "/tenant/v1/issuer/credentials",
        headers=context.config.userdata[issuer]["auth_headers"],
        json=data,
    )
    assert response.status_code == status.HTTP_200_OK, response.__dict__


@then('"{issuer}" will have an "{cred_status}" issuer credential')
def step_impl(context, issuer, cred_status: str):
    response = requests.get(
        context.config.userdata.get("traction_host")
        + "/tenant/v1/issuer/credentials"
        + f"?status={cred_status}",
        headers=context.config.userdata[issuer]["auth_headers"],
    )
    assert response.status_code == status.HTTP_200_OK, response.__dict__
    resp_json = json.loads(response.content)
    assert len(resp_json["items"]) == 1, resp_json
    context.config.userdata[issuer]["issuer_credential"] = resp_json["items"][0]


@when('"{issuer}" revokes credential from "{holder}"')
def step_impl(context, issuer, holder):
    issuer_credential = context.config.userdata[issuer]["issuer_credential"]
    issuer_credential_id = issuer_credential["issuer_credential_id"]

    revocation_comment = "revoking for bdd test"
    data = {
        "issuer_credential_id": issuer_credential_id,
        "comment": revocation_comment,
    }

    response = requests.post(
        context.config.userdata.get("traction_host")
        + f"/tenant/v1/issuer/credentials/{issuer_credential_id}/revoke-credential",
        headers=context.config.userdata[issuer]["auth_headers"],
        json=data,
    )
    assert response.status_code == status.HTTP_200_OK, response.__dict__
    resp_json = json.loads(response.content)
    assert resp_json["item"] is not None
    assert resp_json["item"]["status"] == "Revoked"
    assert resp_json["item"]["contact"]["alias"] == holder
    assert resp_json["item"]["revocation_comment"] == revocation_comment


## COMPOSED ACTIONS
@given('"{tenant}" is an issuer')
def step_impl(context, tenant):
    context.execute_steps(
        f"""
    Given "{tenant}" is allowed to be an issuer by the innkeeper
    And we sadly wait for {10} seconds because we have not figured out how to listen for events
    And "{tenant}" registers as an issuer
    And we sadly wait for {5} seconds because we have not figured out how to listen for events
    And "{tenant}" will have a public did   
    """
    )
