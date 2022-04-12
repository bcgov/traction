import asyncio
import json
import requests
import time
from behave import *
from behave.api.async_step import async_run_until_complete
from aiohttp import ClientSession, ContentTypeError
from starlette import status


@given('"{inviter}" generates a connection invitation for "{invitee}"')
@when('"{inviter}" generates a connection invitation for "{invitee}"')
def step_impl(context, inviter: str, invitee: str):
    response = requests.post(
        context.config.userdata.get("traction_host")
        + "/tenant/v0/connections/create-invitation",
        params={"alias": invitee},
        headers=context.config.userdata[inviter]["auth_headers"],
    )
    resp_json = json.loads(response.content)
    response.status_code == status.HTTP_200_OK, resp_json
    context.config.userdata[inviter]["invitation"] = json.loads(
        resp_json["connection"]["invitation"]
    )


@given('"{invitee}" receives the invitation from "{inviter}"')
@when('"{invitee}" receives the invitation from "{inviter}"')
def step_impl(context, invitee: str, inviter: str):
    response = requests.post(
        context.config.userdata.get("traction_host")
        + "/tenant/v0/connections/receive-invitation",
        params={"alias": inviter},
        json=context.config.userdata[inviter]["invitation"],
        headers=context.config.userdata[invitee]["auth_headers"],
    )
    assert response.status_code == status.HTTP_200_OK, response.status
    resp_json = json.loads(response.content)
    # wait for events
    time.sleep(1)


@then('"{tenant}" has a connection to "{tenant_2}" in state "{connection_state}"')
def step_impl(context, tenant, tenant_2, connection_state):
    response = requests.get(
        context.config.userdata.get("traction_host") + "/tenant/v0/connections",
        params={"alias": tenant_2},
        headers=context.config.userdata[tenant]["auth_headers"],
    )
    assert response.status_code == status.HTTP_200_OK, response.status
    resp_json = json.loads(response.content)
    assert len(resp_json) == 1, context.table
    assert resp_json[0]["state"] == connection_state, resp_json[0]
    # wait for events
    time.sleep(1)


## COMPOSED ACTIONS
@given('"{tenant_1}" and "{tenant_2}" are connected')
def step_impl(context, tenant_1, tenant_2):
    context.execute_steps(
        f"""
    Given "{tenant_1}" generates a connection invitation for "{tenant_2}"
    And "{tenant_2}" receives the invitation from "{tenant_1}"
    """
    )
