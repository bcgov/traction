import pytest
import json
import pprint
from tests.db.tenant_factory import TenantFactory
from api.db.repositories.tenants import TenantsRepository
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.testclient import TestClient


pp = pprint.PrettyPrinter()


@pytest.mark.asyncio
async def test_tenants_get_all(client: TestClient, test_session: AsyncSession) -> None:
    _repo = TenantsRepository(test_session)
    test_tenant = TenantFactory.build()
    test_session.add(test_tenant)
    await test_session.commit()
    pp.pprint(await _repo.find())
    resp = client.get("/v1/innkeeper/tenants")

    assert resp.ok
    resp_content = json.loads(resp.content)

    pp.pprint(resp_content)
    pp.pprint(client.__dict__)
    pp.pprint(test_session.__dict__)

    assert len(resp_content) == 1
