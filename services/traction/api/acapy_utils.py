from aiohttp import (
    ClientSession,
    ClientResponse,
)
import json
from starlette_context import context

from config import Config


def get_acapy_headers(headers=None, tenant=False) -> dict:
    """Return HTTP headers required for aca-py admin call."""

    if not headers:
        headers = {}
    if not headers.get("accept"):
        headers["accept"] = "application/json"
    if not headers.get("Content-Type"):
        headers["Content-Type"] = "application/json"
    if Config.ACAPY_ADMIN_URL_API_KEY:
        headers["X-API-Key"] = Config.ACAPY_ADMIN_URL_API_KEY
    try:
        if tenant and context.get("TENANT_WALLET_TOKEN"):
            headers["Authorization"] = "Bearer " + context.get("TENANT_WALLET_TOKEN")
    except Exeption as e:
        # TODO bit of a hack, throws an exception if the middlewares are called in teh wrong order
        pass
    return headers


def is_tenant() -> bool:
    """
    Check if running in aca-py tenant mode.
    """
    try:
        return context.get("TENANT_WALLET_TOKEN") is not None
    except:
        # TODO bit of a hack, throws an exception if the middlewares are called in teh wrong order
        return False


async def acapy_admin_request(
    method, path, data=None, text=False, params=None, headers=None, tenant=False
) -> ClientResponse:
    """
    Generic routine to call an Aca-Py admin api.

    Default headers are used if not supplied, and security headers are injected.

    Args:
        method: http method (i.e. GET, POST, etc)
        path: endpoint path (e.g. /multitenancy/wallet)
        data: json object to POST (default None)
        text: expect a plaintext response (default False which means json response)
        params: dict of query params to include in request
        headers: dict of headers to include in the request (default None)
        tenant: whether request is in context of a tenant (default False)

    Returns:
        aiohttp response object
    """
    params = {k: v for (k, v) in (params or {}).items() if v is not None}
    url = f"{Config.ACAPY_ADMIN_URL}/{path}"

    # TODO where should this live, and how do we want to handle HTTP sessions?
    async with ClientSession() as client_session:
        headers = get_acapy_headers(headers, tenant)
        async with client_session.request(
            method,
            url,
            json=data,
            params=params,
            headers=headers,
        ) as resp:
            resp_text = await resp.text()
            try:
                resp.raise_for_status()
            except Exception as e:
                # try to retrieve and print text on error
                raise Exception(f"Error: {resp_text}") from e
            if not resp_text and not text:
                return None
            if not text:
                try:
                    return json.loads(resp_text)
                except json.JSONDecodeError as e:
                    raise Exception(f"Error decoding JSON: {resp_text}") from e
            return resp_text


async def acapy_agency_GET(
    path, text=False, params=None, headers=None
) -> ClientResponse:
    """
    Call an Aca-Py agency endpoint using GET method.
    """

    if is_tenant():
        raise Exception("Error can't call agency admin when accessing as a tenant")
    response = await acapy_admin_request(
        "GET", path, data=None, text=text, params=params, headers=headers, tenant=False
    )
    return response


async def acapy_agency_POST(
    path, data=None, text=False, params=None, headers=None
) -> ClientResponse:
    """
    Call an Aca-Py agency endpoint using POST method.
    """

    if is_tenant():
        raise Exception("Error can't call agency admin when accessing as a tenant")
    response = await acapy_admin_request(
        "POST", path, data=data, text=text, params=params, headers=headers, tenant=False
    )
    return response


async def acapy_agency_PUT(
    path, data=None, text=False, params=None, headers=None
) -> ClientResponse:
    """
    Call an Aca-Py agency endpoint using PUT method.
    """

    if is_tenant():
        raise Exception("Error can't call agency admin when accessing as a tenant")
    response = await acapy_admin_request(
        "PUT", path, data=data, text=text, params=params, headers=headers, tenant=False
    )
    return response


async def acapy_GET(path, text=False, params=None, headers=None) -> ClientResponse:
    """
    Call an Aca-Py tenant endpoint using GET method.
    """

    if not is_tenant():
        raise Exception("Error can't call tenant admin when accessing as an innkeeper")
    response = await acapy_admin_request(
        "GET", path, data=None, text=text, params=params, headers=headers, tenant=True
    )
    return response


async def acapy_POST(
    path, data=None, text=False, params=None, headers=None
) -> ClientResponse:
    """
    Call an Aca-Py tenant endpoint using POST method.
    """

    if not is_tenant():
        raise Exception("Error can't call tenant admin when accessing as an innkeeper")
    response = await acapy_admin_request(
        "POST", path, data=data, text=text, params=params, headers=headers, tenant=True
    )
    return response


async def acapy_PATCH(path, text=False, params=None, headers=None) -> ClientResponse:
    """
    Call an Aca-Py tenant endpoint using PATCH method.
    """

    if not is_tenant():
        raise Exception("Error can't call tenant admin when accessing as an innkeeper")
    response = await acapy_admin_request(
        "PATCH", path, data=None, text=text, params=params, headers=headers, tenant=True
    )
    return response


async def acapy_PUT(
    path, data=None, text=False, params=None, headers=None
) -> ClientResponse:
    """
    Call an Aca-Py tenant endpoint using PUT method.
    """

    if not is_tenant():
        raise Exception("Error can't call tenant admin when accessing as an innkeeper")
    response = await acapy_admin_request(
        "PUT", path, data=data, text=text, params=params, headers=headers, tenant=True
    )
    return response


# TODO in case we need them, we have implemented these specific utility functions previously:
# async def admin_GET_FILE(self, path, params=None, headers=None) -> bytes:
# async def admin_PUT_FILE(self, files, url, params=None, headers=None) -> bytes:
