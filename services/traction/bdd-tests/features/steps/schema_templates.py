import json
from behave import *
from starlette import status

from v1_api import *


@given('"{tenant}" creates schema template(s)')
def step_impl(context, tenant: str):
    for row in context.table:
        # | name  | version | attributes | tag | revocation_enabled |
        name = row["name"]
        version = row["version"]
        attributes = row["attributes"].split(",")

        payload = {
            "schema_definition": {
                "schema_name": name,
                "schema_version": version,
                "attributes": attributes,
            },
            "name": name,
            "tags": [],
        }

        if row["tag"]:
            # API will set lowest value for registry size if revocation enabled
            payload["credential_definition"] = {
                "tag": row["tag"],
                "revocation_enabled": row["revocation_enabled"],
                "revocation_registry_size": 0,
            }

        response = create_schema_template(context, tenant, payload)
        assert response.status_code == status.HTTP_200_OK, response.__dict__

        resp_json = json.loads(response.content)

        context.config.userdata[tenant].setdefault("governance", {})
        context.config.userdata[tenant]["governance"].setdefault("schema_templates", {})
        context.config.userdata[tenant]["governance"].setdefault(
            "credential_templates", {}
        )
        context.config.userdata[tenant]["governance"]["schema_templates"][
            name
        ] = resp_json["item"]
        if "credential_item" in resp_json:
            context.config.userdata[tenant]["governance"]["credential_templates"][
                name
            ] = resp_json["credential_item"]

        assert response.status_code == status.HTTP_200_OK, response.__dict__


@given('"{tenant}" cannot create a schema template')
def step_impl(context, tenant: str):
    payload = {
        "schema_definition": {
            "schema_name": "not an issuer",
            "schema_version": "0.1",
            "attributes": ["first", "last"],
        },
        "name": "not an issuer",
        "tags": [],
    }
    response = create_schema_template(context, tenant, payload)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED, response.__dict__


@then('"{tenant}" will have {count:d} schema template(s)')
def step_impl(context, tenant: str, count: int):
    params = {}
    response = list_schema_templates(context, tenant, params)
    assert response.status_code == status.HTTP_200_OK, response.__dict__
    resp_json = json.loads(response.content)
    assert resp_json["total"] == count, resp_json


@step('"{tenant}" will list schema template(s) with credential templates')
def step_impl(context, tenant: str):
    params = {"credential_templates": True}
    response = list_schema_templates(context, tenant, params)
    assert response.status_code == status.HTTP_200_OK, response.__dict__
    resp_json = json.loads(response.content)
    count = 0
    for s in resp_json["items"]:
        count = count + len(s["credential_templates"])
    assert count > 0, resp_json["items"]


@then('"{tenant}" will have {count:d} credential template(s)')
def step_impl(context, tenant: str, count: int):
    params = {}
    response = list_credential_templates(context, tenant, params)
    assert response.status_code == status.HTTP_200_OK, response.__dict__
    resp_json = json.loads(response.content)
    assert resp_json["total"] == count, resp_json


@then('"{tenant}" can find schema template "{name}" by name')
def step_impl(context, tenant: str, name: str):
    params = {"name": name}
    response = list_schema_templates(context, tenant, params)
    assert response.status_code == status.HTTP_200_OK, response.__dict__
    resp_json = json.loads(response.content)
    assert len(resp_json["items"]) == 1, resp_json
    assert resp_json["items"][0]["name"] == name


@then('"{tenant}" can find schema template "{name}" by tags "{tags}"')
def step_impl(context, tenant: str, name: str, tags: str):
    params = {"tags": tags, "name": name}
    response = list_schema_templates(context, tenant, params)
    assert response.status_code == status.HTTP_200_OK, response.__dict__
    resp_json = json.loads(response.content)
    assert len(resp_json["items"]) == 1, resp_json
    assert resp_json["items"][0]["name"] == name
    _tags = [x.strip() for x in tags.split(",")]
    for t in _tags:
        assert t in resp_json["items"][0]["tags"]


@then('"{tenant}" can find schema template "{name}" by schema_id')
def step_impl(context, tenant: str, name: str):
    schema_template = context.config.userdata[tenant]["governance"]["schema_templates"][
        name
    ]
    params = {"schema_id": schema_template["schema_id"]}
    response = list_schema_templates(context, tenant, params)
    assert response.status_code == status.HTTP_200_OK, response.__dict__
    resp_json = json.loads(response.content)
    assert len(resp_json["items"]) == 1, resp_json
    assert resp_json["items"][0]["schema_id"] == schema_template["schema_id"]


@then('"{tenant}" cannot schema template find "{name}" by name')
def step_impl(context, tenant: str, name: str):
    params = {"name": name}
    response = list_schema_templates(context, tenant, params)
    assert response.status_code == status.HTTP_200_OK, response.__dict__
    resp_json = json.loads(response.content)
    assert len(resp_json["items"]) == 0, resp_json


@then('"{tenant}" can find schema template "{name}" with deleted flag')
def step_impl(context, tenant: str, name: str):
    params = {"name": name, "deleted": True}
    response = list_schema_templates(context, tenant, params)
    assert response.status_code == status.HTTP_200_OK, response.__dict__
    resp_json = json.loads(response.content)
    assert len(resp_json["items"]) == 1, resp_json
    assert resp_json["items"][0]["name"] == name
    assert resp_json["items"][0]["deleted"]
    assert resp_json["items"][0]["status"] == "Deleted"


@then('"{tenant}" can get schema template "{name}" by schema_template_id')
def step_impl(context, tenant: str, name: str):
    schema_template = context.config.userdata[tenant]["governance"]["schema_templates"][
        name
    ]
    response = get_schema_template(
        context, tenant, schema_template["schema_template_id"]
    )
    assert response.status_code == status.HTTP_200_OK, response.__dict__
    resp_json = json.loads(response.content)
    assert (
        resp_json["item"]["schema_template_id"] == schema_template["schema_template_id"]
    )


@then('"{tenant}" can update schema template "{name}"')
def step_impl(context, tenant: str, name: str):
    schema_template = context.config.userdata[tenant]["governance"]["schema_templates"][
        name
    ]
    payload = {"schema_template_id": schema_template["schema_template_id"]}

    for row in context.table:
        attribute = row["attribute"]
        value = row["value"]
        if attribute == "tags":
            value = row["value"].split(",")

        payload[attribute] = value

    response = update_schema_template(
        context, tenant, schema_template["schema_template_id"], payload
    )
    assert response.status_code == status.HTTP_200_OK, response.__dict__
    resp_json = json.loads(response.content)
    item = resp_json["item"]
    assert item["schema_template_id"] == schema_template["schema_template_id"]
    for row in context.table:
        attribute = row["attribute"]
        value = row["value"]
        if attribute == "tags":
            value = row["value"].split(",")

        assert item[attribute] == value


@then('"{tenant}" can delete schema template "{name}"')
def step_impl(context, tenant: str, name: str):
    schema_template = context.config.userdata[tenant]["governance"]["schema_templates"][
        name
    ]
    response = delete_schema_template(
        context, tenant, schema_template["schema_template_id"]
    )
    assert response.status_code == status.HTTP_200_OK, response.__dict__
    resp_json = json.loads(response.content)
    item = resp_json["item"]
    assert item["schema_template_id"] == schema_template["schema_template_id"]
    assert item["deleted"]
    assert item["status"] == "Deleted"


@then('"{tenant}" cannot find schema template "{name}" by schema_id')
def step_impl(context, tenant: str, name: str):
    schema_template = context.config.userdata[tenant]["governance"]["schema_templates"][
        name
    ]
    params = {"schema_id": schema_template["schema_id"]}
    response = list_schema_templates(context, tenant, params)
    assert response.status_code == status.HTTP_200_OK, response.__dict__
    resp_json = json.loads(response.content)
    assert len(resp_json["items"]) == 0, resp_json


@then('"{tenant}" cannot get schema template "{name}" by schema_template_id')
def step_impl(context, tenant: str, name: str):
    schema_template = context.config.userdata[tenant]["governance"]["schema_templates"][
        name
    ]
    response = get_schema_template(
        context, tenant, schema_template["schema_template_id"]
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND, response.__dict__


@then('"{tenant}" can get schema template "{name}" with deleted flag')
def step_impl(context, tenant: str, name: str):
    schema_template = context.config.userdata[tenant]["governance"]["schema_templates"][
        name
    ]
    params = {"deleted": True}
    response = get_schema_template(
        context, tenant, schema_template["schema_template_id"], params
    )
    assert response.status_code == status.HTTP_200_OK, response.__dict__
    resp_json = json.loads(response.content)
    assert (
        resp_json["item"]["schema_template_id"] == schema_template["schema_template_id"]
    )
    assert resp_json["item"]["deleted"]
    assert resp_json["item"]["status"] == "Deleted"


@step('"{tenant}" can get schema template "{name}" with "{status_code}" status')
def step_impl(context, tenant: str, name: str, status_code: str):
    schema_template = context.config.userdata[tenant]["governance"]["schema_templates"][
        name
    ]
    params = {}
    response = get_schema_template(
        context, tenant, schema_template["schema_template_id"], params
    )
    assert response.status_code == status.HTTP_200_OK, response.__dict__
    resp_json = json.loads(response.content)
    assert (
        resp_json["item"]["schema_template_id"] == schema_template["schema_template_id"]
    )
    assert resp_json["item"]["status"] == "Error"
    assert resp_json["item"]["error_status_detail"] is not None
