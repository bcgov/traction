import json
from behave import *
from starlette import status
from v1_api import *


@step('innkeeper can get "{tenant}" permissions')
def step_impl(context, tenant: str):
    response = innkeeper_get_permissions(context, tenant)
    assert response.status_code == status.HTTP_200_OK, response.__dict__
    resp_json = json.loads(response.content)
    item = resp_json["item"]
    for row in context.table:
        name = row["name"]
        value = convert_value(row["value"])

        assert item[name] == value, row
    tenant_id = context.config.userdata[tenant]["tenant_id"]
    assert item["tenant_id"] == tenant_id


@step('innkeeper can update "{tenant}" permissions')
def step_impl(context, tenant: str):
    payload = {}
    for row in context.table:
        name = row["name"]
        value = row["value"]

        payload[name] = convert_value(value)

    response = innkeeper_update_permissions(context, tenant, payload)
    assert response.status_code == status.HTTP_200_OK, response.__dict__
    resp_json = json.loads(response.content)
    item = resp_json["item"]
    for row in context.table:
        name = row["name"]
        value = convert_value(row["value"])

        assert item[name] == value
    tenant_id = context.config.userdata[tenant]["tenant_id"]
    assert item["tenant_id"] == tenant_id
