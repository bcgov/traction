import uuid
from typing import List

import pytest

from pydantic import parse_obj_as

from api.db.models.tenant import TenantRead
from api.db.models.tenant_issuer import TenantIssuerRead
from api.endpoints.models.innkeeper import CheckInRequest, CheckInResponse

from httpx import AsyncClient

from tests.test_utils import innkeeper_auth, innkeeper_headers, random_string

pytestmark = pytest.mark.asyncio


async def checkin_tenant(test_client: AsyncClient) -> (CheckInResponse, dict):
    # use this method for everything except testing check-in API
    bearer_token = await innkeeper_auth(test_client)
    headers = innkeeper_headers(bearer_token)
    checkin = CheckInRequest(name=random_string("tenant_test_", 12))
    resp = await test_client.post(
        "/innkeeper/v0/check-in", headers=headers, json=checkin.dict()
    )
    checkin_resp = CheckInResponse(**resp.json())
    return checkin_resp, headers


@pytest.mark.integtest
async def test_check_in(test_client: AsyncClient) -> None:
    async def api_call(headers, json):
        resp = await test_client.post(
            url="/innkeeper/v0/check-in", headers=headers, json=json
        )
        return resp

    bearer_token = await innkeeper_auth(test_client)
    headers = innkeeper_headers(bearer_token)

    checkin = CheckInRequest(name=random_string("tenant_test_", 12))

    resp = await api_call(headers=headers, json=checkin.dict())
    assert resp.status_code == 201, resp.content

    # ASSERT
    checkin_resp = CheckInResponse(**resp.json())
    assert checkin_resp.wallet_id is not None and checkin_resp.wallet_key is not None

    # ASSERT - no security...
    checkin2 = CheckInRequest(name=random_string("tenant_test_", 12))
    resp = await api_call(headers={}, json=checkin2.dict())
    assert resp.status_code == 401

    # ASSERT - name is unique
    resp = await api_call(headers=headers, json=checkin.dict())
    assert resp.status_code == 409

    # ASSERT - name is mandatory...
    checkin.name = None
    resp = await api_call(headers=headers, json=checkin.dict())
    assert resp.status_code == 422


@pytest.mark.integtest
async def test_get_tenant(test_client: AsyncClient) -> None:
    async def api_call(headers, id):
        resp = await test_client.get(
            url=f"/innkeeper/v0/tenants/{id}",
            headers=headers,
        )
        return resp

    (checkin_resp, headers) = await checkin_tenant(test_client)

    # ACT
    resp = await api_call(headers=headers, id=checkin_resp.id)
    assert resp.status_code == 200, resp.content

    # ASSERT
    tenant = TenantRead(**resp.json())
    assert str(tenant.id) == str(checkin_resp.id)

    # ASSERT - no security...
    resp = await api_call(headers={}, id=checkin_resp.id)
    assert resp.status_code == 401

    # ASSERT - bad id (not uuid)
    bad_id = "badid"
    resp = await api_call(headers=headers, id=bad_id)
    assert resp.status_code == 422

    # ASSERT - id not exists
    uuid_id = uuid.uuid4()
    resp = await api_call(headers=headers, id=uuid_id)
    assert resp.status_code == 404


@pytest.mark.integtest
async def test_get_tenants(test_client: AsyncClient) -> None:
    async def api_call(headers):
        resp = await test_client.get(
            url="/innkeeper/v0/tenants",
            headers=headers,
        )
        return resp

    (checkin_resp, headers) = await checkin_tenant(test_client)

    # get list of tenants...
    resp = await api_call(headers=headers)
    assert resp.status_code == 200, resp.content

    results = parse_obj_as(List[TenantRead], resp.json())
    assert len(results) > 0, len(results)
    # the new tenant should be in the results...
    assert next((x for x in results if str(x.id) == str(checkin_resp.id)), None)

    # ASSERT - no security...
    resp = await api_call(headers={})
    assert resp.status_code == 401


@pytest.mark.integtest
async def test_make_issuer(test_client: AsyncClient) -> None:
    async def api_call(headers, id):
        resp = await test_client.post(
            url=f"/innkeeper/v0/issuers/{id}",
            headers=headers,
        )
        return resp

    (checkin_resp, headers) = await checkin_tenant(test_client)

    # make this tenant an issuer...
    resp = await api_call(headers=headers, id=checkin_resp.id)
    assert resp.status_code == 200, resp.content

    # ASSERT - no security...
    resp = await api_call(headers={}, id=checkin_resp.id)
    assert resp.status_code == 401

    # ASSERT - bad id (not uuid)
    bad_id = "badid"
    resp = await api_call(headers=headers, id=bad_id)
    assert resp.status_code == 422

    # ASSERT - id not exists
    uuid_id = uuid.uuid4()
    resp = await api_call(headers=headers, id=uuid_id)
    assert resp.status_code == 404


@pytest.mark.integtest
async def test_get_issuer(test_client: AsyncClient) -> None:
    async def api_call(headers, id):
        resp = await test_client.get(
            url=f"/innkeeper/v0/issuers/{id}",
            headers=headers,
        )
        return resp

    (checkin_resp, headers) = await checkin_tenant(test_client)

    # make this tenant an issuer...
    resp = await test_client.post(
        f"/innkeeper/v0/issuers/{checkin_resp.id}", headers=headers
    )
    assert resp.status_code == 200, resp.content

    # get issuer by id
    resp = await api_call(headers=headers, id=checkin_resp.id)
    assert resp.status_code == 200, resp.content

    issuer = TenantIssuerRead(**resp.json())
    assert str(issuer.tenant_id) == str(checkin_resp.id)
    assert str(issuer.wallet_id) == str(checkin_resp.wallet_id)

    # ASSERT - no security...
    resp = await api_call(headers={}, id=checkin_resp.id)
    assert resp.status_code == 401

    # ASSERT - bad id (not uuid)
    bad_id = "badid"
    resp = await api_call(headers=headers, id=bad_id)
    assert resp.status_code == 422

    # ASSERT - id not exists
    uuid_id = uuid.uuid4()
    resp = await api_call(headers=headers, id=uuid_id)
    assert resp.status_code == 404


@pytest.mark.integtest
async def test_get_issuers(test_client: AsyncClient) -> None:
    async def api_call(headers):
        resp = await test_client.get(
            url="/innkeeper/v0/issuers",
            headers=headers,
        )
        return resp

    (checkin_resp, headers) = await checkin_tenant(test_client)

    # make this tenant an issuer...
    resp = await test_client.post(
        f"/innkeeper/v0/issuers/{checkin_resp.id}", headers=headers
    )
    assert resp.status_code == 200, resp.content

    # get list of issuers...
    resp = await api_call(headers=headers)
    assert resp.status_code == 200, resp.content

    results = parse_obj_as(List[TenantIssuerRead], resp.json())
    assert len(results) > 0, len(results)
    # the new issuer should be in the results...
    assert next((x for x in results if str(x.tenant_id) == str(checkin_resp.id)), None)

    # ASSERT - no security...
    resp = await api_call(headers={})
    assert resp.status_code == 401
