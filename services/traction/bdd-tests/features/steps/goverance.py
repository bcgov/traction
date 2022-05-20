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

        response_data = get_governance_schemas(
            context, tenant, cred_def_state, schema_name
        )
        if any(
            schema["cred_def_state"] == cred_def_state
            and schema["schema_name"] == schema_name
            for schema in response_data["items"]
        ):
            ex_result_found = True
            break

    assert (
        ex_result_found
    ), f"after {timeout} seconds, tenant_schema found was {response_data}"

    # while we are here, update context.governance
    context.config.userdata.setdefault("governance", {})

    context.config.userdata["governance"]["schemas"] = {
        i["schema_name"]: i for i in response_data["items"]
    }
    print(f"Polled for {tenant} seconds")


# @given(
#     '"{tenant}" has a tenant_schema record with a cred_def status of "{cred_def_state}" for "{schema_name}"'
# )
# @then(
#     '"{tenant}" will have a tenant_schema record with a cred_def status of "{cred_def_state}" for "{schema_name}"'
# )
def get_governance_schemas(context, tenant: str, cred_def_state: str, schema_name: str):

    response = requests.get(
        context.config.userdata.get("traction_host") + "/tenant/v1/governance/schemas",
        headers=context.config.userdata[tenant]["auth_headers"],
    )
    assert response.status_code == status.HTTP_200_OK, response.__dict__

    content = json.loads(response.content)

    assert len(content["items"]) > 0, content
    return content
