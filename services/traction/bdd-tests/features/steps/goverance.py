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
        "schema_definition": {
            "schema_name": schema_name,
            "schema_version": "0.1",
            "attributes": [row["attr"] for row in context.table],
        },
        "name": schema_name,
        "tags": [],
        "credential_definition": {
            "tag": cred_def_tag,
            "revocation_enabled": False,
            "revocation_registry_size": 0,
        },
    }

    response = requests.post(
        context.config.userdata.get("traction_host")
        + "/tenant/v1/governance/schema_templates/",
        json=payload,
        headers=context.config.userdata[issuer]["auth_headers"],
    )
    resp_json = json.loads(response.content)

    context.config.userdata[issuer].setdefault("schema_template", resp_json["item"])
    context.config.userdata[issuer].setdefault(
        "credential_template", resp_json["credential_template"]
    )

    assert response.status_code == status.HTTP_200_OK, response.__dict__


@given(
    'check "{tenant}" for {timeout} seconds for a cred_def status of "{cred_def_state}" for "{schema_name}"'
)
@then(
    'check "{tenant}" for {timeout} seconds for a cred_def status of "{cred_def_state}" for "{schema_name}"'
)
def step_impl(
    context,
    tenant: str,
    timeout: str,  # don't know how to make an int natively
    cred_def_state: str,
    schema_name: str,
):
    ex_result_found = False
    timeout = int(timeout)
    check_period = (
        float(timeout / 20) if timeout > 20 else 1
    )  # only check maximum of 20 times
    time_passed = 0
    while time_passed < timeout:
        time.sleep(check_period)
        time_passed = time_passed + check_period

        response_data = get_credential_template(context, tenant)
        ex_result_found = response_data["state"] == cred_def_state
        if ex_result_found:
            break

    assert (
        ex_result_found
    ), f"after {time_passed} seconds, credential_template found was {response_data}"

    print(f"Polled for {timeout} seconds")


def get_credential_template(context, tenant: str):

    credential_template_id = context.config.userdata[tenant]["credential_template"][
        "credential_template_id"
    ]
    response = requests.get(
        context.config.userdata.get("traction_host")
        + f"/tenant/v1/governance/credential_templates/{credential_template_id}",
        headers=context.config.userdata[tenant]["auth_headers"],
    )
    assert response.status_code == status.HTTP_200_OK, response.__dict__

    content = json.loads(response.content)

    assert content["item"] is not None
    context.config.userdata[tenant]["credential_template"] = content["item"]
    return content["item"]
