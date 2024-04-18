import requests
from random_word import RandomWords

from utils import wait_a_bit
from config import PROXY_URL
from storage import tenants_store

r = RandomWords()


async def set_public_did(tenant):
    tenant_headers = {"Authorization": f"Bearer {tenant['token']}"}
    tenant_name = tenant["tenant"]["tenant_name"]

    data = None
    res = requests.post(
        f"{PROXY_URL}/tenant/endorser-connection",
        headers=tenant_headers,
        json=data,
    )

    wait_a_bit(10)

    data = None
    res = requests.get(
        f"{PROXY_URL}/tenant/endorser-connection",
        headers=tenant_headers,
        json=data,
    )
    # now we expect there to be a connection

    # ==============================================
    print("\ntenant (issuer) create public did...\n")

    data = {"method": "sov", "options": {"key_type": "ed25519"}}
    res = requests.post(
        f"{PROXY_URL}/wallet/did/create", headers=tenant_headers, json=data
    )
    wallet_did_create_result = res.json()["result"]
    wallet_create_did = wallet_did_create_result["did"]
    wallet_create_verkey = wallet_did_create_result["verkey"]

    # register did
    data = None
    res = requests.post(
        f"{PROXY_URL}/ledger/register-nym?did={wallet_create_did}&verkey={wallet_create_verkey}&alias={tenant_name}",
        headers=tenant_headers,
        json=data,
    )

    wait_a_bit(5)

    # public did
    data = None
    res = requests.post(
        f"{PROXY_URL}/wallet/did/public?did={wallet_create_did}",
        headers=tenant_headers,
        json=data,
    )

    wait_a_bit()

    # get public did
    res = requests.get(
        f"{PROXY_URL}/wallet/did/public", headers=tenant_headers, json=data
    )
    wallet_public_did_result = res.json()["result"]
    public_did = wallet_public_did_result["did"]
    # let's store the public did for demo purposes...
    # this could always get fetched via the api
    tenant["public_did"] = public_did
    tenants_store[tenant_name] = tenant
    return public_did
