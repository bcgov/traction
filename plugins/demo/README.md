TBD - this will have docker-compose and different configs for various scenarios (different plugins, different acapy configs etc)
it should build image(s) based on ../docker/Dockerfile

We need more and varied configurations, and we need to parameterize the compose file (port numbers, passwords etc).

Currently will run at localhost:3000 (http), localhost:3001 (admin), and localhost:3002 (websockets).
Loads up a postgres database for acapy (localhost:5432).
Runs tenant proxy (localhost:8032).


### build and run
```
cd demo
docker-compose build
docker-compose up
```

### down and cleanup
```
cd demo
docker-compose down
docker-compose down -v --remove-orphans
```

### simple python script
Copy this, install dependencies however you prefer, and run against the demo instance.

This will illustrate the registration and check-in process between the innkeeper and a tenant.

```python
import time

import requests
from random_word import RandomWords

r = RandomWords()
"""
install these dependencies - poetry, pip, whatever...

requests = "^2.28.2"
Random-Word = "^1.0.11"

script is based on running acapy with traction plugins using the default demo local environment.

see https://github.com/bcgov/traction/tree/develop/plugins/demo
"""

# default configuration for local development...
PROXY_URL = "http://localhost:8032"
INNKEEPER_TENANT_ID = "innkeeper"
INNKEEPER_WALLET_KEY = "change-me"


def wait_a_bit(secs: int = 1):
    print(f"... wait {secs} seconds ...")
    time.sleep(secs)


if __name__ == "__main__":

    # ==============================================
    print("\nlog in innkeeper tenant...\n")

    # get innkeeper token
    data = {
        "wallet_key": INNKEEPER_WALLET_KEY,
    }
    res = requests.post(
        f"{PROXY_URL}/multitenancy/tenant/{INNKEEPER_TENANT_ID}/token", json=data
    )
    innkeeper_token = res.json()["token"]
    print(f"innkeeper_token = {innkeeper_token}")

    # ==============================================
    print("\ncreate a reservation (issuer)...\n")

    reservation_name = r.get_random_word()
    print(f"reservation_name = {reservation_name}")
    data = {
        "contact_email": "fake@bad.good",
        "contact_name": reservation_name,
        "contact_phone": "555-5555",
        "tenant_name": reservation_name,
        "tenant_reason": "testing...",
    }
    res = requests.post(f"{PROXY_URL}/multitenancy/reservations", json=data)
    reservation_id = res.json()["reservation_id"]
    print(f"reservation_id = {reservation_id}")

    print("\ninnkeeper approve the reservation...\n")

    data = {
        "state_notes": "go for it",
    }
    innkeeper_headers = {"Authorization": f"Bearer {innkeeper_token}"}
    res = requests.put(
        f"{PROXY_URL}/innkeeper/reservations/{reservation_id}/approve",
        headers=innkeeper_headers,
        json=data,
    )
    reservation_pwd = res.json()["reservation_pwd"]
    print(reservation_pwd)

    print("\ntenant (issuer) check-in and get keys (token)...\n")

    data = {
        "reservation_pwd": reservation_pwd,
    }
    res = requests.post(
        f"{PROXY_URL}/multitenancy/reservations/{reservation_id}/check-in", json=data
    )
    reservation_result = res.json()
    print(f"reservation_result = {reservation_result}")
    tenant_token = reservation_result["token"]
    print(f"tenant_token = {tenant_token}")
    tenant_headers = {"Authorization": f"Bearer {tenant_token}"}

    data = None
    res = requests.get(
        f"{PROXY_URL}/tenant", headers=tenant_headers, json=data
    )
    get_tenant_result = res.json()
    print(f"get_tenant_result = {get_tenant_result}")

```
