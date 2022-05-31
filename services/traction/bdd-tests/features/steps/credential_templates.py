import json
import time

from behave import *
from starlette import status

from v1_api import *


@then(
    'wait {timeout:d} seconds until "{tenant}" can create credential template for "{name}"'
)
def step_impl(
    context,
    timeout: int,
    tenant: str,
    name: str,
):
    schema_template = context.config.userdata[tenant]["governance"]["schema_templates"][
        name
    ]

    ex_result_found = False
    timeout = int(timeout)
    check_period = float(timeout / 20) if timeout > 20 else 1
    time_passed = 0
    while time_passed < timeout:
        time.sleep(check_period)
        time_passed = time_passed + check_period

        response = get_schema_template(
            context, tenant, schema_template["schema_template_id"]
        )
        resp_json = json.loads(response.content)
        ex_result_found = resp_json["item"]["status"] == "Active"
        if ex_result_found:
            break

    assert (
        ex_result_found
    ), f"after {time_passed} seconds, schema_template found was {resp_json}"

    print(f"Polled for {timeout - time_passed} seconds")


@given('"{tenant}" creates credential template for "{name}" by schema_id')
def step_impl(context, tenant: str, name: str):
    schema_template = context.config.userdata[tenant]["governance"]["schema_templates"][
        name
    ]

    payload = {
        "credential_definition": {
            "tag": "default",
            "revocation_enabled": False,
            "revocation_registry_size": 0,
        },
        "schema_id": schema_template["schema_id"],
        "name": name,
        "tags": [],
    }
    response = create_credential_template(context, tenant, payload)
    assert response.status_code == status.HTTP_200_OK, response.__dict__

    resp_json = json.loads(response.content)

    context.config.userdata[tenant]["governance"]["credential_templates"][
        name
    ] = resp_json["item"]


@given('"{tenant}" creates credential template for "{name}" by schema_template_id')
def step_impl(context, tenant: str, name: str):
    schema_template = context.config.userdata[tenant]["governance"]["schema_templates"][
        name
    ]

    payload = {
        "credential_definition": {
            "tag": "default",
            "revocation_enabled": False,
            "revocation_registry_size": 0,
        },
        "schema_template_id": schema_template["schema_template_id"],
        "name": name,
        "tags": [],
    }
    response = create_credential_template(context, tenant, payload)
    assert response.status_code == status.HTTP_200_OK, response.__dict__

    resp_json = json.loads(response.content)

    context.config.userdata[tenant]["governance"]["credential_templates"][
        name
    ] = resp_json["item"]


@given('"{tenant}" cannot create a credential template')
def step_impl(context, tenant: str):
    payload = {
        "credential_definition": {
            "tag": "default",
            "revocation_enabled": False,
            "revocation_registry_size": 0,
        },
        "schema_id": "do not need one",
        "name": "cannot create",
        "tags": [],
    }
    response = create_credential_template(context, tenant, payload)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED, response.__dict__


@then('"{tenant}" can find credential template "{name}" by name')
def step_impl(context, tenant: str, name: str):
    params = {"name": name}
    response = list_credential_templates(context, tenant, params)
    assert response.status_code == status.HTTP_200_OK, response.__dict__
    resp_json = json.loads(response.content)
    assert len(resp_json["items"]) == 1, resp_json
    assert resp_json["items"][0]["name"] == name


@then('"{tenant}" can find credential template "{name}" by schema_id')
def step_impl(context, tenant: str, name: str):
    schema_template = context.config.userdata[tenant]["governance"]["schema_templates"][
        name
    ]
    params = {"schema_id": schema_template["schema_id"]}
    response = list_credential_templates(context, tenant, params)
    assert response.status_code == status.HTTP_200_OK, response.__dict__
    resp_json = json.loads(response.content)
    assert len(resp_json["items"]) == 1, resp_json
    assert resp_json["items"][0]["schema_id"] == schema_template["schema_id"]


@then('"{tenant}" can find credential template "{name}" by cred_def_id')
def step_impl(context, tenant: str, name: str):
    credential_template = context.config.userdata[tenant]["governance"][
        "credential_templates"
    ][name]
    params = {"cred_def_id": credential_template["cred_def_id"]}
    response = list_credential_templates(context, tenant, params)
    assert response.status_code == status.HTTP_200_OK, response.__dict__
    resp_json = json.loads(response.content)
    assert len(resp_json["items"]) == 1, resp_json
    assert resp_json["items"][0]["cred_def_id"] == credential_template["cred_def_id"]


@then('"{tenant}" cannot credential template find "{name}" by name')
def step_impl(context, tenant: str, name: str):
    params = {"name": name}
    response = list_credential_templates(context, tenant, params)
    assert response.status_code == status.HTTP_200_OK, response.__dict__
    resp_json = json.loads(response.content)
    assert len(resp_json["items"]) == 0, resp_json


@then('"{tenant}" can find credential template "{name}" with deleted flag')
def step_impl(context, tenant: str, name: str):
    params = {"name": name, "deleted": True}
    response = list_credential_templates(context, tenant, params)
    assert response.status_code == status.HTTP_200_OK, response.__dict__
    resp_json = json.loads(response.content)
    assert len(resp_json["items"]) == 1, resp_json
    assert resp_json["items"][0]["name"] == name
    assert resp_json["items"][0]["deleted"]
    assert resp_json["items"][0]["status"] == "Deleted"


@then('"{tenant}" can get credential template "{name}" by credential_template_id')
def step_impl(context, tenant: str, name: str):
    credential_template = context.config.userdata[tenant]["governance"][
        "credential_templates"
    ][name]
    response = get_credential_template(
        context, tenant, credential_template["credential_template_id"]
    )
    assert response.status_code == status.HTTP_200_OK, response.__dict__
    resp_json = json.loads(response.content)
    assert (
        resp_json["item"]["credential_template_id"]
        == credential_template["credential_template_id"]
    )


@then('"{tenant}" can update credential template "{name}"')
def step_impl(context, tenant: str, name: str):
    credential_template = context.config.userdata[tenant]["governance"][
        "credential_templates"
    ][name]
    payload = {"credential_template_id": credential_template["credential_template_id"]}

    for row in context.table:
        attribute = row["attribute"]
        value = row["value"]
        if attribute == "tags":
            value = row["value"].split(",")

        payload[attribute] = value

    response = update_credential_template(
        context, tenant, credential_template["credential_template_id"], payload
    )
    assert response.status_code == status.HTTP_200_OK, response.__dict__
    resp_json = json.loads(response.content)
    item = resp_json["item"]
    assert (
        item["credential_template_id"] == credential_template["credential_template_id"]
    )
    for row in context.table:
        attribute = row["attribute"]
        value = row["value"]
        if attribute == "tags":
            value = row["value"].split(",")

        assert item[attribute] == value


@then('"{tenant}" can delete credential template "{name}"')
def step_impl(context, tenant: str, name: str):
    credential_template = context.config.userdata[tenant]["governance"][
        "credential_templates"
    ][name]
    response = delete_credential_template(
        context, tenant, credential_template["credential_template_id"]
    )
    assert response.status_code == status.HTTP_200_OK, response.__dict__
    resp_json = json.loads(response.content)
    item = resp_json["item"]
    assert (
        item["credential_template_id"] == credential_template["credential_template_id"]
    )
    assert item["deleted"]
    assert item["status"] == "Deleted"


@then('"{tenant}" cannot find credential template "{name}" by cred_def_id')
def step_impl(context, tenant: str, name: str):
    credential_template = context.config.userdata[tenant]["governance"][
        "credential_templates"
    ][name]
    params = {"cred_def_id": credential_template["cred_def_id"]}
    response = list_credential_templates(context, tenant, params)
    assert response.status_code == status.HTTP_200_OK, response.__dict__
    resp_json = json.loads(response.content)
    assert len(resp_json["items"]) == 0, resp_json


@then('"{tenant}" cannot get credential template "{name}" by credential_template_id')
def step_impl(context, tenant: str, name: str):
    credential_template = context.config.userdata[tenant]["governance"][
        "credential_templates"
    ][name]
    response = get_credential_template(
        context, tenant, credential_template["credential_template_id"]
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND, response.__dict__


@then('"{tenant}" can get credential template "{name}" with deleted flag')
def step_impl(context, tenant: str, name: str):
    credential_template = context.config.userdata[tenant]["governance"][
        "credential_templates"
    ][name]
    params = {"deleted": True}
    response = get_credential_template(
        context, tenant, credential_template["credential_template_id"], params
    )
    assert response.status_code == status.HTTP_200_OK, response.__dict__
    resp_json = json.loads(response.content)
    assert (
        resp_json["item"]["credential_template_id"]
        == credential_template["credential_template_id"]
    )
    assert resp_json["item"]["deleted"]
    assert resp_json["item"]["status"] == "Deleted"
