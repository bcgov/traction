def test_main(client):
    assert True


def test_hello_world(client):
    resp = client.get("/")
    assert resp.ok
