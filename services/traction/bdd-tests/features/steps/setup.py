import random, string, asyncio

from behave import *
from behave.api.async_step import async_run_until_complete
from aiohttp import ClientSession, ContentTypeError
from starlette.exceptions import HTTPException
from starlette import status


@given("we have authenticated at the innkeeper")
@async_run_until_complete
async def get_innkeeper_token(context):
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

    async with ClientSession() as client_session:
        async with await client_session.post(
            url=token_url,
            data=data,
            headers=headers,
        ) as response:
            try:
                resp = await response.json()
                token = resp["access_token"]
                context.config.userdata["innkeeper_auth_headers"] = {
                    "accept": "application/json",
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {token}",
                }
            except ContentTypeError:
                text = await response.text()
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=text,
                )


@given("we have {n} traction tenants")
@when("we have {n} traction tenants")
@async_run_until_complete
@asyncio.coroutine
async def create_traction_tenants(context, n):
    rand_suffix = "-" + "".join(random.choice(string.ascii_letters) for i in range(6))

    for row in context.table:
        tenant_name = row["name"] + rand_suffix

        async with ClientSession() as client_session:
            # create tenant
            async with await client_session.post(
                context.config.userdata.get("traction_host") + "/innkeeper/v0/check-in",
                json={"name": tenant_name},
                headers=context.config.userdata["innkeeper_auth_headers"],
            ) as check_in_response:
                assert check_in_response.status == status.HTTP_201_CREATED
                check_in_json = await check_in_response.json()
                # authenticate and save token to context
                headers = {
                    "accept": "application/json",
                    "Content-Type": "application/x-www-form-urlencoded",
                }

                data = {
                    "username": check_in_json["wallet_id"],
                    "password": check_in_json["wallet_key"],
                    "grant_type": "",
                    "scope": "",
                }

                async with await client_session.post(
                    context.config.userdata.get("traction_host") + "/tenant/token",
                    headers=headers,
                    data=data,
                ) as tenant_auth_response:
                    resp = await tenant_auth_response.json()
                    assert tenant_auth_response.status == status.HTTP_200_OK, resp
                    token = resp["access_token"]

        context.config.userdata[row["name"]] = {
            "role": row["role"],
            "name": tenant_name,
            "wallet_id": check_in_json["wallet_id"],
            "wallet_key": check_in_json["wallet_key"],
            "auth_headers": {
                "accept": "application/json",
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}",
            },
        }
