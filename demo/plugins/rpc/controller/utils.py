import requests
import plugins.rpc.controller.config as config


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
        f"{config.PROXY_URL}/multitenancy/tenant{config.INNKEEPER_TENANT_ID}/token",
        json=data,
    )

    return res.json().get("token")


async def create_tenant(tenant_name: str):
    """Create a tenant."""

    # Tenant creates a reservation request
    res = requests.post(
        f"{config.PROXY_URL}/multitenancy/reservations",
        json={"name": tenant_name, "email": "asdf@asdf.com"},
    )
    reservation_id = res.json().get("reservation_id")

    # Innkeeper approves the reservation request
    res = requests.post(
        f"{config.PROXY_URL}/multitenancy/tenant{reservation_id}/approve",
        headers=await get_innkeeper_auth_headers(),
        json={},
    )
    reservation_pwd = res.json().get("reservation_pwd")

    # Tenant can now create their wallet
    res = requests.post(
        f"{config.PROXY_URL}/multitenancy/tenant{reservation_id}/checki-in",
        json={"reservation_pwd": reservation_pwd},
    )
    json_res = res.json()

    return {
        "token": json_res.get("token"),
        "wallet_id": json_res.get("wallet_id"),
        "wallet_key": json_res.get("wallet_key"),
    }
