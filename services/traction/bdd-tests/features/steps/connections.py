import json
import requests
import time
import pprint
from behave import *
from starlette import status


@given('"{inviter}" generates a connection invitation for "{invitee}"')
@when('"{inviter}" generates a connection invitation for "{invitee}"')
def step_impl(context, inviter: str, invitee: str):
    response = requests.post(
        context.config.userdata.get("traction_host")
        + "/tenant/v1/contacts/create-invitation",
        json={"alias": invitee},
        headers=context.config.userdata[inviter]["auth_headers"],
    )
    assert response.status_code == status.HTTP_200_OK, response.__dict__

    resp_json = json.loads(response.content)
    response.status_code == status.HTTP_200_OK, resp_json
    context.config.userdata[inviter]["invitation"] = {
        "invitation": resp_json["invitation"],
        "invitation_url": resp_json["invitation_url"],
    }


@given('"{inviter}" creates a multi-use invitation')
@when('"{inviter}" creates a multi-use invitation')
def step_impl(context, inviter: str):
    response = requests.post(
        context.config.userdata.get("traction_host")
        + "/tenant/v1/invitations/create-multi-use-invitation",
        json={"name": "testing"},
        headers=context.config.userdata[inviter]["auth_headers"],
    )
    assert response.status_code == status.HTTP_200_OK, response.__dict__

    resp_json = json.loads(response.content)
    response.status_code == status.HTTP_200_OK, resp_json
    context.config.userdata[inviter]["invitation"] = {
        "invitation": resp_json["item"]["acapy"]["invitation"],
        "invitation_url": resp_json["invitation_url"],
    }


@given('"{invitee}" receives the invitation from "{inviter}"')
@when('"{invitee}" receives the invitation from "{inviter}"')
def step_impl(context, invitee: str, inviter: str):
    data = {"alias": inviter, **context.config.userdata[inviter]["invitation"]}
    response = requests.post(
        context.config.userdata.get("traction_host")
        + "/tenant/v1/contacts/receive-invitation",
        json=data,
        headers=context.config.userdata[invitee]["auth_headers"],
    )
    assert response.status_code == status.HTTP_200_OK, response.status
    resp_json = json.loads(response.content)
    time.sleep(5)


@given('"{tenant}" has a connection to "{tenant_2}" in status "{contact_status}"')
@then('"{tenant}" has a connection to "{tenant_2}" in status "{contact_status}"')
def step_impl(context, tenant, tenant_2, contact_status):
    response = requests.get(
        context.config.userdata.get("traction_host") + "/tenant/v1/contacts",
        params={"alias": tenant_2},
        headers=context.config.userdata[tenant]["auth_headers"],
    )
    assert response.status_code == status.HTTP_200_OK, response.status
    resp_json = json.loads(response.content)
    assert len(resp_json["items"]) == 1, resp_json
    assert resp_json["items"][0]["status"] == contact_status, resp_json["items"][0]
    # while we are here, update connection context for this tenant
    context.config.userdata[tenant]["connections"] = {
        c["alias"]: c for c in resp_json["items"]
    }


## COMPOSED ACTIONS
@given('"{tenant_1}" and "{tenant_2}" are connected')
def step_impl(context, tenant_1, tenant_2):
    context.execute_steps(
        f"""
    Given "{tenant_1}" generates a connection invitation for "{tenant_2}"
    And "{tenant_2}" receives the invitation from "{tenant_1}"
    And "{tenant_1}" has a connection to "{tenant_2}" in status "Active"
    And "{tenant_2}" has a connection to "{tenant_1}" in status "Active"
    """
    )
