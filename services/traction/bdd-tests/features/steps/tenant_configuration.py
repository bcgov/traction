import json
from behave import *
from starlette import status
from v1_api import *

@step('"{tenant}" can get their configuration')
def step_impl(context, tenant: str):
    response = tenant_get_configuration(context, tenant)
    assert response.status_code == status.HTTP_200_OK, response.__dict__
    resp_json = json.loads(response.content)
    item = resp_json["item"]
    for row in context.table:
        name = row["name"]
        value = convert_value(row["value"])

        assert item[name] == value, row


@step('"{tenant}" can update value(s)')
def step_impl(context, tenant: str):
    payload = {}
    for row in context.table:
        name = row["name"]
        value = row["value"]

        payload[name] = convert_value(value)

    response = tenant_update_configuration(context, tenant, payload)
    assert response.status_code == status.HTTP_200_OK, response.__dict__
    resp_json = json.loads(response.content)
    item = resp_json["item"]
    for row in context.table:
        name = row["name"]
        value = convert_value(row["value"])

        assert item[name] == value
