import json
import requests
import time

from behave import *
from starlette import status


@given(
    '"{issuer}" writes a new schema "{schema_name}" and cred def tagged "{cred_def_tag}"'
)
@when(
    '"{issuer}" writes a new schema "{schema_name}" and cred def tagged "{cred_def_tag}"'
)
def step_impl(context, issuer: str, schema_name: str, cred_def_tag: str):

    payload = {
        "schema_request": {
            "schema_name": schema_name,
            "schema_version": "0.1",
            "attributes": [row["attr"] for row in context.table],
        },
        "cred_def_tag": cred_def_tag,
        "revocable": False,
    }

    response = requests.post(
        context.config.userdata.get("traction_host") + "/tenant/v1/governance/schemas/",
        json=payload,
        headers=context.config.userdata[issuer]["auth_headers"],
    )
    assert response.status_code == status.HTTP_200_OK, response.__dict__


@given(
    '"{tenant}" has a tenant_schema record with an "{cred_def_state}" cred_def for "{schema_name}"'
)
@then(
    '"{tenant}" will have a tenant_schema record with an "{cred_def_state}" cred_def for "{schema_name}"'
)
def step_impl(context, tenant: str, cred_def_state: str, schema_name: str):

    response = requests.get(
        context.config.userdata.get("traction_host") + "/tenant/v1/governance/schemas",
        headers=context.config.userdata[tenant]["auth_headers"],
    )
    assert response.status_code == status.HTTP_200_OK, response.__dict__

    content = json.loads(response.content)

    assert len(content["items"]) > 0, content

    # while we are here, update context.governance
    context.config.userdata["governance"] = {
        "schemas": {i["schema_name"]: i for i in content["items"]}
    }
    assert any(
        schema["schema_state"] == "completed"
        and schema["cred_def_state"] == cred_def_state
        and schema["schema_name"] == schema_name
        for schema in content["items"]
    ), response.__dict__
