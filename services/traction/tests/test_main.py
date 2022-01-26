from tests import client


def test_main():
    assert True


def test_hello_world():
    resp = client.get("/")
    assert resp.ok
