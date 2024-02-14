import requests

from . import config


def get_tenant_auth_headers(token):
    """Get the auth headers for the tenant."""

    return {"Authorization": f"Bearer {token}"}


async def get_innkeeper_auth_headers():
    """Get the auth headers for the innkeeper."""

    return {"Authorization": f"Bearer {await get_inkeeper_token()}"}


async def get_inkeeper_token():
    """Get the token for the innkeeper."""

    data = {"wallet_key": config.INNKEEPER_WALLET_KEY}

    res = requests.post(
        f"{config.PROXY_URL}/multitenancy/tenant/{config.INNKEEPER_TENANT_ID}/token",
        json=data,
    )

    return res.json().get("token")


async def create_tenant(tenant_name: str):
    """Create a tenant."""

    # Tenant creates a reservation request, it will auto approve
    res = requests.post(
        f"{config.PROXY_URL}/multitenancy/reservations",
        json={"tenant_name": tenant_name, "contact_email": "asdf@asdf.com"},
    )
    reservation_id = res.json().get("reservation_id")
    reservation_pwd = res.json().get("reservation_pwd")

    # Tenant can now create their wallet
    res = requests.post(
        f"{config.PROXY_URL}/multitenancy/reservations/{reservation_id}/check-in",
        json={"reservation_pwd": reservation_pwd},
    )
    json_res = res.json()

    return {
        "tenant_name": tenant_name,
        "token": json_res.get("token"),
        "wallet_id": json_res.get("wallet_id"),
        "wallet_key": json_res.get("wallet_key"),
    }


async def create_invitation(headers):
    """Create an out-of-band invitation for the tenant."""

    res = requests.post(
        f"{config.PROXY_URL}/out-of-band/create-invitation",
        headers=headers,
        params={"auto_accept": "true"},
        json={
            "handshake_protocols": ["https://didcomm.org/didexchange/1.0"],
        },
    )

    return res.json()

async def create_connection(headers, invitation):
    """Create a connection with the invitation."""

    res = requests.post(
        f"{config.PROXY_URL}/out-of-band/receive-invitation",
        headers=headers,
        json=invitation,
    )

    return res.json()