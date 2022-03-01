import logging
from typing import Optional
from uuid import UUID

from aiohttp import ClientSession, ContentTypeError
from starlette import status
from starlette.exceptions import HTTPException

from api.core.config import settings
from api.core.utils import hash_password
from api.db.models import Tenant
from api.services import traction_urls as t_urls

logger = logging.getLogger(__name__)


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
                logger.exception("Error getting token", exc_info=True)
                text = await response.text()
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=text,
                )


async def create_tenant(name: str):
    auth_headers = await get_auth_headers()
    # name, we will set the webhook url with security afterward.
    data = {"name": name}
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
                logger.exception("Error creating tenant", exc_info=True)
                text = await response.text()
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=text,
                )


async def create_tenant_webhook(tenant: Tenant):
    # here we connect as the tenant, passing in their traction credentials.
    auth_headers = await get_auth_headers(tenant.wallet_id, tenant.wallet_key)
    # set the webhook up with security
    # in a real LOB, do not use your wallet_key, configure it in a vault or env secret.
    # must simpler in the showcase to do this...
    hashed_wallet_key = hash_password(str(tenant.wallet_key))
    data = {
        "webhook_url": f"{settings.SHOWCASE_ENDPOINT}/api/v1/webhook/{tenant.id}",
        "webhook_key": hashed_wallet_key,
        "config": {"acapy": True},
    }
    # TODO: error handling calling Traction
    async with ClientSession() as client_session:
        async with await client_session.post(
            url=t_urls.TENANT_ADMIN_WEBHOOK,
            json=data,
            headers=auth_headers,
        ) as response:
            try:
                resp = await response.json()
                return resp
            except ContentTypeError:
                logger.exception("Error creating tenant webhook", exc_info=True)
                text = await response.text()
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
    query_params = {}
    if alias:
        query_params = {"alias": alias}

    # TODO: error handling calling Traction
    async with ClientSession() as client_session:
        async with await client_session.get(
            url=t_urls.TENANT_GET_CONNECTIONS,
            params=query_params,
            json=data,
            headers=auth_headers,
        ) as response:
            try:
                resp = await response.json()
                return resp
            except ContentTypeError:
                logger.exception(
                    "Error getting connections list",
                    exc_info=True,
                )
                text = await response.text()
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
    query_params = {"alias": alias, "invitation_type": "didexchange/1.0"}
    # TODO: error handling calling Traction
    async with ClientSession() as client_session:
        async with await client_session.post(
            url=t_urls.TENANT_CREATE_INVITATION,
            params=query_params,
            json=data,
            headers=auth_headers,
        ) as response:
            try:
                resp = await response.json()
                return resp
            except ContentTypeError:
                logger.exception("Error creating invitation", exc_info=True)
                text = await response.text()
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=text,
                )


async def accept_invitation(
    wallet_id: UUID, wallet_key: UUID, alias: str, invitation: dict
):
    # call Traction to accept an invitation...
    auth_headers = await get_auth_headers(wallet_id=wallet_id, wallet_key=wallet_key)
    query_params = {"alias": alias}
    # TODO: error handling calling Traction
    async with ClientSession() as client_session:
        async with await client_session.post(
            url=t_urls.TENANT_RECEIVE_INVITATION,
            params=query_params,
            json=invitation,
            headers=auth_headers,
        ) as response:
            try:
                resp = await response.json()
                return resp
            except ContentTypeError:
                logger.exception("Error accepting invitation", exc_info=True)
                text = await response.text()
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=text,
                )


async def innkeeper_make_issuer(tenant_id: UUID):
    # call Traction to accept an invitation...
    innkeeper_auth_headers = await get_auth_headers()
    # TODO: error handling calling Traction
    async with ClientSession() as client_session:
        async with await client_session.post(
            url=t_urls.INNKEEPER_MAKE_ISSUER + f"/{tenant_id}",
            headers=innkeeper_auth_headers,
        ) as response:
            try:
                resp = await response.json()
                return resp
            except ContentTypeError:
                logger.exception("Error registering tenant as issuer", exc_info=True)
                text = await response.text()
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=text,
                )


async def tenant_admin_issuer(wallet_id: UUID, wallet_key: UUID, tenant_id: UUID):
    auth_headers = await get_auth_headers(wallet_id=wallet_id, wallet_key=wallet_key)
    # TODO: error handling calling Traction
    async with ClientSession() as client_session:
        async with await client_session.post(
            url=t_urls.TENANT_MAKE_ISSUER,
            headers=auth_headers,
        ) as response:
            try:
                resp = await response.json()
                return resp
            except ContentTypeError:
                logger.exception("Error registering self as issuer", exc_info=True)
                text = await response.text()
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=text,
                )


async def tenant_create_schema(
    wallet_id: UUID,
    wallet_key: UUID,
    schema: dict = None,
    schema_id: str = None,
    cred_def_tag: str = None,
):
    auth_headers = await get_auth_headers(wallet_id=wallet_id, wallet_key=wallet_key)
    data = schema
    params = {}
    if schema_id is not None:
        params["schema_id"] = schema_id
    if cred_def_tag is not None:
        params["cred_def_tag"] = cred_def_tag
    async with ClientSession() as client_session:
        async with await client_session.post(
            url=t_urls.TENANT_CREATE_SCHEMA,
            headers=auth_headers,
            params=params,
            json=data,
        ) as response:
            try:
                resp = await response.json()
                return resp
            except ContentTypeError:
                logger.exception(
                    "Error creating schema/credential definition", exc_info=True
                )
                text = await response.text()
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=text,
                )


async def tenant_issue_credential(
    wallet_id: UUID,
    wallet_key: UUID,
    connection_id: str,
    alias: str,
    cred_def_id: str,
    attributes: list = [],
):
    auth_headers = await get_auth_headers(wallet_id=wallet_id, wallet_key=wallet_key)
    data = {"attributes": attributes}
    params = {
        "cred_protocol": "v1.0",
        "cred_def_id": cred_def_id,
        "connection_id": connection_id,
        "alias": alias,
    }
    async with ClientSession() as client_session:
        async with await client_session.post(
            url=t_urls.TENANT_CREDENTIAL_ISSUE,
            headers=auth_headers,
            params=params,
            json=data,
        ) as response:
            try:
                resp = await response.json()
                return resp
            except ContentTypeError:
                logger.exception("Error issuing credential", exc_info=True)
                text = await response.text()
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=text,
                )


async def tenant_get_issue_credentials(
    wallet_id: UUID,
    wallet_key: UUID,
):
    auth_headers = await get_auth_headers(wallet_id=wallet_id, wallet_key=wallet_key)
    async with ClientSession() as client_session:
        async with await client_session.get(
            url=t_urls.TENANT_CREDENTIAL_ISSUE,
            headers=auth_headers,
        ) as response:
            try:
                resp = await response.json()
                return resp
            except ContentTypeError:
                logger.exception("Error getting credentials", exc_info=True)
                text = await response.text()
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=text,
                )
