from tests import client


def test_tenants_get_all():
    resp = client.get("/v1/innkeeper/tenants")
    assert resp.ok
