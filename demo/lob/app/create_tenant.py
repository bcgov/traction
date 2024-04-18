import requests
from random_word import RandomWords

from config import INNKEEPER_WALLET_KEY, PROXY_URL, INNKEEPER_TENANT_ID, WEBHOOK_URL
from storage import innkeeper_store

r = RandomWords()


async def create_tenant(tenant_name: str):
    # ==============================================
    # need the innkeeper to automate reservation + approval + checkin
    innkeeper_headers = innkeeper_store["headers"]
    innkeeper_token = innkeeper_store["token"]
    # get innkeeper_store token
    if innkeeper_token is None:
        data = {
            "wallet_key": INNKEEPER_WALLET_KEY,
        }
        res = requests.post(
            f"{PROXY_URL}/multitenancy/tenant/{INNKEEPER_TENANT_ID}/token", json=data
        )
        innkeeper_token = res.json()["token"]
        innkeeper_headers = {"Authorization": f"Bearer {innkeeper_token}"}
        innkeeper_store["token"] = innkeeper_token
        innkeeper_store["headers"] = innkeeper_headers

    # ==============================================
    # tenant to create a reservation...
    data = {
        "contact_email": "fake@bad.good",
        "tenant_name": tenant_name,
    }
    res = requests.post(f"{PROXY_URL}/multitenancy/reservations", json=data)
    reservation_id = res.json()["reservation_id"]

    # innkeeper to approve the reservation request...
    data = {
        "state_notes": "welcome",
    }
    res = requests.put(
        f"{PROXY_URL}/innkeeper/reservations/{reservation_id}/approve",
        headers=innkeeper_headers,
        json=data,
    )
    # reservation password would be delivered to tenant in some out of band process...
    reservation_pwd = res.json()["reservation_pwd"]

    # once tenant has reservation password, they can check in (creates wallet)
    data = {
        "reservation_pwd": reservation_pwd,
    }
    res = requests.post(
        f"{PROXY_URL}/multitenancy/reservations/{reservation_id}/check-in", json=data
    )
    reservation_result = res.json()
    token = reservation_result["token"]
    wallet_id = reservation_result["wallet_id"]
    wallet_key = reservation_result["wallet_key"]
    tenant_headers = {"Authorization": f"Bearer {token}"}

    # ok, test out the token by fetching "self"
    data = None
    res = requests.get(f"{PROXY_URL}/tenant", headers=tenant_headers, json=data)
    get_tenant_result = res.json()

    # the tenant needs to update their configuration to tell acapy where to deliver
    # their event data (via webhook)

    # for each tenant, we add a special key to the webhook url
    # theoretically, only the tenant knows what this key is for and can use it to check
    # that the call is made by acapy.
    api_key = r.get_random_word()
    keyed_webhook_url = f"{WEBHOOK_URL}#{api_key}"

    data = {"wallet_webhook_urls": [keyed_webhook_url]}
    res = requests.put(f"{PROXY_URL}/tenant/wallet", headers=tenant_headers, json=data)

    data = None
    res = requests.get(f"{PROXY_URL}/tenant/wallet", headers=tenant_headers, json=data)
    get_wallet_result = res.json()

    return {
        "wallet_id": wallet_id,
        "wallet_key": wallet_key,
        "token": token,
        "tenant": get_tenant_result,
        "wallet": get_wallet_result,
        "api_key": api_key,
        "webhook_data": {},
    }
