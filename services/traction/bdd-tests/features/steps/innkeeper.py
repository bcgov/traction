import random, string, json, pprint

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


@step('innkeeper check-in "{tenant}" with allow_issue_credentials equals "{flag:bool}"')
def step_impl(context, tenant: str, flag: bool):
    rand_suffix = "-" + "".join(random.choice(string.ascii_letters) for i in range(6))
    name = f"{tenant}{rand_suffix}"
    payload = {"name": name, "allow_issue_credentials": flag}
    response = innkeeper_tenants_check_in(context, payload)
    assert response.status_code == status.HTTP_200_OK, response.__dict__
    resp_json = json.loads(response.content)
    pprint.pp(resp_json)
    assert resp_json["item"], resp_json
    tenant_set_auth_headers(context, tenant, resp_json["item"])
    pprint.pp(context.config.userdata[tenant])


@step('innkeeper can find "{count:d}" tenant(s)')
def step_impl(context, count: int):
    for row in context.table:
        public_did_status = row["public_did_status"]
        issuer_status = row["issuer_status"]

        params = {"public_did_status": public_did_status, "issuer_status": issuer_status, "deleted": False}
        response = innkeeper_list_tenants(context, params)
        assert response.status_code == status.HTTP_200_OK, response.__dict__
        resp_json = json.loads(response.content)
        assert len(resp_json["items"]) == count, resp_json
        item = resp_json["items"][0]
        assert item["public_did_status"] == public_did_status, f"public_did_status = {item['public_did_status']}"
        assert item["issuer_status"] == issuer_status, f"issuer_status = {item['issuer_status']}"


@step('innkeeper can get "{tenant}" by tenant_id')
def step_impl(context, tenant: str):
    t = context.config.userdata[tenant]
    response = innkeeper_get_tenant(context, tenant)
    assert response.status_code == status.HTTP_200_OK, response.__dict__
    resp_json = json.loads(response.content)
    pprint.pp(resp_json)
    assert resp_json["item"]["name"] == t["name"], resp_json
