import random, string, requests, json, pprint

from behave import *
from starlette import status


@given("we have authenticated at the innkeeper")
def get_innkeeper_token(context):
    headers = {
        "accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {
        "username": context.config.userdata.get("innkeeper_username"),
        "password": context.config.userdata.get("innkeeper_password"),
        "grant_type": "",
        "scope": "",
    }

    token_url = context.config.userdata.get("traction_host") + "/innkeeper/token"
    # get token
    response = requests.post(
        url=token_url,
        data=data,
        headers=headers,
    )

    assert response.status_code == status.HTTP_200_OK, pprint.pp(response.__dict__)

    resp = json.loads(response.content)
    token = resp["access_token"]

    # save headers to context
    context.config.userdata["innkeeper_auth_headers"] = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }


@step("we have {n} traction tenants")
def create_traction_tenants(context, n):
    rand_suffix = "-" + "".join(random.choice(string.ascii_letters) for i in range(6))

    for row in context.table:
        tenant_name = row["name"] + rand_suffix

        # create tenant
        check_in_response = requests.post(
            context.config.userdata.get("traction_host")
            + "/innkeeper/v1/tenants/check-in",
            json={"name": tenant_name},
            headers=context.config.userdata["innkeeper_auth_headers"],
        )
        assert check_in_response.status_code == status.HTTP_200_OK, pprint.pp(
            check_in_response.__dict__
        )
        check_in_json = json.loads(check_in_response.content)
        tenant = check_in_json["item"]
        # authenticate and save token to context
        headers = {
            "accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
        }

        data = {
            "username": tenant["wallet_id"],
            "password": tenant["wallet_key"],
            "grant_type": "",
            "scope": "",
        }

        tenant_auth_response = requests.post(
            context.config.userdata.get("traction_host") + "/tenant/token",
            headers=headers,
            data=data,
        )

        resp = json.loads(tenant_auth_response.content)
        assert tenant_auth_response.status_code == status.HTTP_200_OK, resp
        auth_token = resp["access_token"]

        # save config to context
        context.config.userdata[row["name"]] = {
            "role": row["role"],
            "name": tenant_name,
            "tenant_id": tenant["tenant_id"],
            "wallet_id": tenant["wallet_id"],
            "wallet_key": tenant["wallet_key"],
            "auth_headers": {
                "accept": "application/json",
                "Content-Type": "application/json",
                "Authorization": f"Bearer {auth_token}",
            },
        }


def _hard_delete_tenant(context, tenant_config: dict):
    delete_response = requests.delete(
        context.config.userdata.get("traction_host")
        + "/innkeeper/v0/tenants/"
        + tenant_config["tenant_id"]
        + "/hard-delete",
        headers=context.config.userdata["innkeeper_auth_headers"],
    )
    assert delete_response.status_code == status.HTTP_204_NO_CONTENT, pprint.pp(
        delete_response.__dict__
    )
    # so that after_scenario won't also try to delete
    tenant_config["deleted"] = True
