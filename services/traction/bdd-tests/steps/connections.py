import asyncio
import json
from multiprocessing import connection
from behave import *
from behave.api.async_step import async_run_until_complete
from aiohttp import ClientSession, ContentTypeError
from starlette.exceptions import HTTPException
from starlette import status


@when('"{inviter}" generates a connection invitation')
@async_run_until_complete
async def step_impl(context, inviter: str):
    async with ClientSession() as client_session:
        response = await client_session.post(
            context.config.userdata.get("traction_host")
            + "/tenant/v0/connections/create-invitation",
            params={"alias": "invitee"},
            headers=context.config.userdata[inviter]["auth_headers"],
        )
        resp_json = await response.json()
        assert response.status == status.HTTP_200_OK, resp_json
    context.config.userdata[inviter]["invitation"] = json.loads(
        resp_json["connection"]["invitation"]
    )


@when('"{invitee}" receives the invitation from "{inviter}"')
@async_run_until_complete
async def step_impl(context, invitee: str, inviter: str):
    async with ClientSession() as client_session:
        response = await client_session.post(
            context.config.userdata.get("traction_host")
            + "/tenant/v0/connections/receive-invitation",
            params={"alias": "inviter"},
            json=context.config.userdata[inviter]["invitation"],
            headers=context.config.userdata[invitee]["auth_headers"],
        )
        assert response.status == status.HTTP_200_OK, response.status
        resp_json = await response.json()
        # wait for events
        await asyncio.sleep(1)


@then('"{tenant}" has a connection in state "{connection_state}"')
@async_run_until_complete
async def step_impl(context, tenant, connection_state):
    async with ClientSession() as client_session:
        response = await client_session.get(
            context.config.userdata.get("traction_host") + "/tenant/v0/connections",
            headers=context.config.userdata[tenant]["auth_headers"],
        )
        assert response.status == status.HTTP_200_OK, response.status
        resp_json = await response.json()
        assert len(resp_json) == 1
        assert resp_json[0]["state"] == connection_state, resp_json[0]
        # wait for events
        await asyncio.sleep(1)
