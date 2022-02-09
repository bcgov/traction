import pytest
import json

from tests.db.tenant_factory import TenantCreateFactory
from api.db.repositories.tenants import TenantsRepository
from sqlalchemy.ext.asyncio import AsyncSession

from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


async def test_tenants_get_all(
    test_client: AsyncClient, db_session: AsyncSession
) -> None:
    # ARRANGE
    _repo = TenantsRepository(db_session=db_session)
    test_tenant = TenantCreateFactory.build()
    pre_count = len(await _repo.find())
    await _repo.create(test_tenant)

    # ACT
    resp = await test_client.get("/innkeeper/v1/tenants")
    assert resp.status_code == 200, resp.content

    # ASSERT
    resp_content = json.loads(resp.content)
    assert len(resp_content) == pre_count + 1, len(resp_content)


async def test_tenants_get_all_6(
    test_client: AsyncClient, db_session: AsyncSession
) -> None:
    # ARRANGE
    _repo = TenantsRepository(db_session=db_session)
    test_tenant = TenantCreateFactory.build()
    pre_count = len(await _repo.find())
    await _repo.create(test_tenant)

    # ACT
    resp = await test_client.get("/innkeeper/v1/tenants")
    assert resp.status_code == 200, resp.content

    # ASSERT
    resp_content = json.loads(resp.content)
    assert len(resp_content) == pre_count + 1, len(resp_content)


async def test_tenants_get_all_4(
    test_client: AsyncClient, db_session: AsyncSession
) -> None:
    # ARRANGE
    _repo = TenantsRepository(db_session=db_session)
    test_tenant = TenantCreateFactory.build()
    await _repo.create(test_tenant)

    # ACT
    resp = await test_client.get("/innkeeper/v1/tenants")
    assert resp.status_code == 200, resp.content

    # ASSERT
    resp_content = json.loads(resp.content)
    assert len(resp_content) == 1, len(resp_content)


async def test_tenants_get_all_3(
    test_client: AsyncClient, db_session: AsyncSession
) -> None:
    # ARRANGE
    _repo = TenantsRepository(db_session=db_session)
    test_tenant = TenantCreateFactory.build()
    await _repo.create(test_tenant)

    # ACT
    resp = await test_client.get("/innkeeper/v1/tenants")
    assert resp.status_code == 200, resp.content

    # ASSERT
    resp_content = json.loads(resp.content)
    assert len(resp_content) == 1, len(resp_content)


async def test_tenants_get_all_2(
    test_client: AsyncClient, db_session: AsyncSession
) -> None:
    # ARRANGE
    _repo = TenantsRepository(db_session=db_session)
    test_tenant = TenantCreateFactory.build()
    await _repo.create(test_tenant)

    # ACT
    resp = await test_client.get("/innkeeper/v1/tenants")
    assert resp.status_code == 200, resp.content

    # ASSERT
    resp_content = json.loads(resp.content)
    assert len(resp_content) == 1, len(resp_content)
