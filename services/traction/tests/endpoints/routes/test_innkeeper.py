import pytest
import json
import pprint
from tests.db.tenant_factory import TenantFactory
from api.db.repositories.tenants import TenantsRepository
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.testclient import TestClient


@pytest.mark.asyncio
async def test_tenants_get_all(client: TestClient, test_session: AsyncSession) -> None:
    _repo = TenantsRepository(test_session)
    test_tenant = TenantFactory.build()
    test_session.add(test_tenant)
    await test_session.commit()

    resp = client.get("/v1/innkeeper/tenants")

    assert resp.ok
    resp_content = json.loads(resp.content)

    pprint.PrettyPrinter().pprint(resp_content)
    pprint.PrettyPrinter().pprint(client.__dict__)
    pprint.PrettyPrinter().pprint(test_session.__dict__)

    assert len(resp_content) == 1
