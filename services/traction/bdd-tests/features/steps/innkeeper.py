import json
from behave import *
from starlette import status
import time
from v1_api import *


@step('"{tenant}" is allowed to be an issuer by the innkeeper')
def step_impl(context, tenant: str):
    response = innkeeper_tenants_make_issuer(context, tenant)
    assert response.status_code == status.HTTP_200_OK, response.__dict__
    # wait for endorser signatures and ledger writes
    time.sleep(20)


@step('innkeeper sets permissions "{permission_name}" to "{flag:bool}" for "{tenant}"')
def step_impl(context, tenant: str, permission_name: str, flag: bool):
    payload = {permission_name: flag}
    response = innkeeper_update_permissions(context, tenant, payload)
    resp_json = json.loads(response.content)
    assert resp_json["item"][permission_name] == flag
