import json
import requests
from behave import *
from starlette import status
from setup import _hard_delete_tenant
import time
from v1_api import *


@step('"{tenant}" is allowed to be an issuer by the innkeeper')
def step_impl(context, tenant: str):
    response = requests.post(
        context.config.userdata.get("traction_host")
        + "/innkeeper/v0/issuers/"
        + context.config.userdata[tenant]["tenant_id"],
        headers=context.config.userdata["innkeeper_auth_headers"],
    )
    assert response.status_code == status.HTTP_200_OK, response.__dict__
    # wait for endorser signatures and ledger writes
    time.sleep(20)


@when('"{tenant}" calls the hard-delete endpoint')
def step_impl(context, tenant: str):
    tenant_config = context.config.userdata[tenant]
    use_fixture(_hard_delete_tenant, context, tenant_config)


@then('"{tenant}" will not exist')
def step_impl(context, tenant: str):
    tenant_id = context.config.userdata[tenant]["tenant_id"]

    response = requests.get(
        context.config.userdata.get("traction_host")
        + "/innkeeper/v0/tenants/"
        + tenant_id,
        headers=context.config.userdata["innkeeper_auth_headers"],
    )
    assert response.status_code == status.HTTP_200_OK, response.__dict__
    assert not json.loads(response.content)["is_active"]


@step('innkeeper sets permissions "{permission_name}" to "{flag:bool}" for "{tenant}"')
def step_impl(context, tenant: str, permission_name: str, flag: bool):
    payload = {permission_name: flag}
    response = innkeeper_update_permissions(context, tenant, payload)
    resp_json = json.loads(response.content)
    assert resp_json["item"][permission_name] == flag
