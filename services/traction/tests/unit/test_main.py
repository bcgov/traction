import pytest

pytestmark = pytest.mark.asyncio


@pytest.mark.integtest
async def test_hello_world(test_client):
    resp = await test_client.get("/")
    assert resp.status_code == 200


async def test_world():
    assert True
