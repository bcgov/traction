import uuid
from typing import List

import pytest

from pydantic import parse_obj_as

from api.db.models.tenant import TenantRead
from api.db.models.tenant_issuer import TenantIssuerRead
from api.endpoints.models.innkeeper import CheckInResponse
from tests.integration.db.tenant_factory import (
    CheckInRequestFactory,
)
from sqlalchemy.ext.asyncio import AsyncSession

from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


@pytest.mark.integtest
async def test_check_in(test_client: AsyncClient, db_session: AsyncSession) -> None:
    # ARRANGE
    checkin = CheckInRequestFactory.build()
    # ACT
    resp = await test_client.post("/innkeeper/v1/check-in", json=checkin.dict())
    assert resp.status_code == 201, resp.content

    # ASSERT
    checkin_resp = CheckInResponse(**resp.json())
    assert checkin_resp.wallet_id is not None and checkin_resp.wallet_key is not None

    # ASSERT - name is unique
    resp = await test_client.post("/innkeeper/v1/check-in", json=checkin.dict())
    assert resp.status_code == 409

    # ASSERT - name is mandatory...
    checkin.name = None
    resp = await test_client.post("/innkeeper/v1/check-in", json=checkin.dict())
    assert resp.status_code == 422


@pytest.mark.integtest
async def test_get_tenant(test_client: AsyncClient, db_session: AsyncSession) -> None:
    # create a tenant
    checkin = CheckInRequestFactory.build()
    resp = await test_client.post("/innkeeper/v1/check-in", json=checkin.dict())
    assert resp.status_code == 201, resp.content

    checkin_resp = CheckInResponse(**resp.json())
    assert checkin_resp.wallet_id is not None and checkin_resp.wallet_key is not None

    # ACT
    resp = await test_client.get(f"/innkeeper/v1/tenants/{checkin_resp.id}")
    assert resp.status_code == 200, resp.content

    # ASSERT
    tenant = TenantRead(**resp.json())
    assert str(tenant.id) == str(checkin_resp.id)

    # ASSERT - bad id (not uuid)
    bad_id = "badid"
    resp = await test_client.get(f"/innkeeper/v1/tenants/{bad_id}")
    assert resp.status_code == 422

    # ASSERT - id not exists
    uuid_id = uuid.uuid4()
    resp = await test_client.get(f"/innkeeper/v1/tenants/{uuid_id}")
    assert resp.status_code == 404


@pytest.mark.integtest
async def test_get_tenants(test_client: AsyncClient, db_session: AsyncSession) -> None:
    # create a tenant
    checkin = CheckInRequestFactory.build()
    resp = await test_client.post("/innkeeper/v1/check-in", json=checkin.dict())
    assert resp.status_code == 201, resp.content

    checkin_resp = CheckInResponse(**resp.json())
    assert checkin_resp.wallet_id is not None and checkin_resp.wallet_key is not None

    # get list of tenants...
    resp = await test_client.get(f"/innkeeper/v1/tenants")
    assert resp.status_code == 200, resp.content

    results = parse_obj_as(List[TenantRead], resp.json())
    assert len(results) > 0, len(results)
    # the new tenant should be in the results...
    assert next((x for x in results if str(x.id) == str(checkin_resp.id)), None)


@pytest.mark.integtest
async def test_make_issuer(test_client: AsyncClient, db_session: AsyncSession) -> None:
    # create a tenant
    checkin = CheckInRequestFactory.build()

    resp = await test_client.post("/innkeeper/v1/check-in", json=checkin.dict())
    assert resp.status_code == 201, resp.content

    checkin_resp = CheckInResponse(**resp.json())
    assert checkin_resp.wallet_id is not None and checkin_resp.wallet_key is not None

    # make this tenant an issuer...
    resp = await test_client.post(f"/innkeeper/v1/issuers/{checkin_resp.id}")
    assert resp.status_code == 200, resp.content


@pytest.mark.integtest
async def test_get_issuer(test_client: AsyncClient, db_session: AsyncSession) -> None:
    # create a tenant
    checkin = CheckInRequestFactory.build()
    resp = await test_client.post("/innkeeper/v1/check-in", json=checkin.dict())
    assert resp.status_code == 201, resp.content

    checkin_resp = CheckInResponse(**resp.json())
    assert checkin_resp.wallet_id is not None and checkin_resp.wallet_key is not None

    # make this tenant an issuer...
    resp = await test_client.post(f"/innkeeper/v1/issuers/{checkin_resp.id}")
    assert resp.status_code == 200, resp.content

    # get issuer by id
    resp = await test_client.get(f"/innkeeper/v1/issuers/{checkin_resp.id}")
    assert resp.status_code == 200, resp.content

    issuer = TenantIssuerRead(**resp.json())
    assert str(issuer.tenant_id) == str(checkin_resp.id)
    assert str(issuer.wallet_id) == str(checkin_resp.wallet_id)


@pytest.mark.integtest
async def test_get_issuers(test_client: AsyncClient, db_session: AsyncSession) -> None:
    # create a tenant
    checkin = CheckInRequestFactory.build()
    resp = await test_client.post("/innkeeper/v1/check-in", json=checkin.dict())
    assert resp.status_code == 201, resp.content

    checkin_resp = CheckInResponse(**resp.json())
    assert checkin_resp.wallet_id is not None and checkin_resp.wallet_key is not None

    # make this tenant an issuer...
    resp = await test_client.post(f"/innkeeper/v1/issuers/{checkin_resp.id}")
    assert resp.status_code == 200, resp.content

    # get list of issuers...
    resp = await test_client.get(f"/innkeeper/v1/issuers")
    assert resp.status_code == 200, resp.content

    results = parse_obj_as(List[TenantIssuerRead], resp.json())
    assert len(results) > 0, len(results)
    # the new issuer should be in the results...
    assert next((x for x in results if str(x.tenant_id) == str(checkin_resp.id)), None)
