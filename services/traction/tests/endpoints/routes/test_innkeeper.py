import pytest
from tests.db.tenant_factory import TenantFactory
from api.db.repositories.tenants import TenantsRepository


@pytest.mark.asyncio
async def test_tenants_get_all(client, test_session):
    _repo = TenantsRepository(test_session)
    test_tenant = TenantFactory.build()
    out_tenant = await _repo.create(test_tenant)
    print(test_tenant)
    print(out_tenant)
    resp = client.get("/v1/innkeeper/tenants")
    assert resp.ok
    assert False
