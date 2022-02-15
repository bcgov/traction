import urllib
from typing import Optional
from uuid import UUID

from aiohttp import ClientSession, ContentTypeError
from starlette import status
from starlette.exceptions import HTTPException

from api.core.config import settings
from api.services import traction_urls as t_urls


async def get_auth_headers(
    wallet_id: Optional[UUID] = None, wallet_key: Optional[UUID] = None
):
    username = str(wallet_id) if wallet_id else settings.TRACTION_API_ADMIN_USER
    password = str(wallet_key) if wallet_key else settings.TRACTION_API_ADMIN_KEY
    token_url = t_urls.TENANT_TOKEN if wallet_id else t_urls.INNKEEPER_TOKEN

    headers = {
        "accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {
        "username": username,
        "password": password,
        "grant_type": "",
        "scope": "",
    }

    # TODO: error handling calling Traction
    async with ClientSession() as client_session:
        async with await client_session.post(
            url=token_url,
            data=data,
            headers=headers,
        ) as response:
            try:
                resp = await response.json()
                token = resp["access_token"]
                return {
                    "accept": "application/json",
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {token}",
                }
            except ContentTypeError:
                text = await resp.text()
                print(text)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=text,
                )


async def create_tenant(name: str):
    auth_headers = await get_auth_headers()
    # name and webhook_url
    data = {
        "name": name,
        "webhook_url": f"{settings.SHOWCASE_ENDPOINT}/api/v1/webhook",
    }
    # TODO: error handling calling Traction
    async with ClientSession() as client_session:
        async with await client_session.post(
            url=t_urls.INNKEEPER_CHECKIN,
            json=data,
            headers=auth_headers,
        ) as response:
            try:
                resp = await response.json()
                return resp
            except ContentTypeError:
                text = await resp.text()
                print(text)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=text,
                )


async def get_connections(
    wallet_id: UUID,
    wallet_key: UUID,
    alias: Optional[str] = None,
):
    auth_headers = await get_auth_headers(wallet_id=wallet_id, wallet_key=wallet_key)
    # no body...
    data = {}
    url = f"{t_urls.TENANT_GET_CONNECTIONS}"
    if alias:
        query_params = urllib.parse.urlencode({"alias": alias})
        url = f"{t_urls.TENANT_GET_CONNECTIONS}?{query_params}"

    # TODO: error handling calling Traction
    async with ClientSession() as client_session:
        async with await client_session.get(
            url=url,
            json=data,
            headers=auth_headers,
        ) as response:
            try:
                resp = await response.json()
                return resp
            except ContentTypeError:
                text = await resp.text()
                print(text)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=text,
                )


async def create_invitation(
    wallet_id: UUID,
    wallet_key: UUID,
    alias: str,
):
    # call Traction to create an invitation...
    auth_headers = await get_auth_headers(wallet_id=wallet_id, wallet_key=wallet_key)
    # no body...
    data = {}
    query_params = urllib.parse.urlencode(
        {"alias": alias, "invitation_type": "didexchange/1.0"}
    )
    url = f"{t_urls.TENANT_CREATE_INVITATION}?{query_params}"
    # TODO: error handling calling Traction
    async with ClientSession() as client_session:
        async with await client_session.post(
            url=url,
            json=data,
            headers=auth_headers,
        ) as response:
            try:
                resp = await response.json()
                return resp
            except ContentTypeError:
                text = await resp.text()
                print(text)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=text,
                )


async def accept_invitation(
    wallet_id: UUID, wallet_key: UUID, alias: str, invitation: dict
):
    # call Traction to accept an invitation...
    auth_headers = await get_auth_headers(wallet_id=wallet_id, wallet_key=wallet_key)
    query_params = urllib.parse.urlencode({"alias": alias})
    url = f"{t_urls.TENANT_RECEIVE_INVITATION}?{query_params}"
    # TODO: error handling calling Traction
    async with ClientSession() as client_session:
        async with await client_session.post(
            url=url,
            json=invitation,
            headers=auth_headers,
        ) as response:
            try:
                resp = await response.json()
                return resp
            except ContentTypeError:
                text = await resp.text()
                print(text)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=text,
                )
