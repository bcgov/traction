import string
import random
import os
import json

from httpx import AsyncClient


def random_string(prefix: str, length: int = 10) -> str:
    letters = string.ascii_lowercase
    return prefix + "".join(random.choice(letters) for i in range(length))


async def innkeeper_auth(test_client: AsyncClient) -> str:
    username = os.environ.get("TRACTION_API_ADMIN_USER", "innkeeper")
    password = os.environ.get("TRACTION_API_ADMIN_KEY", "change-me")
    data = {"username": username, "password": password}
    token_resp = await test_client.post("/innkeeper/token", data=data)
    assert token_resp.status_code == 200, token_resp.content
    token_content = json.loads(token_resp.content)
    bearer_token = "Bearer " + token_content["access_token"]

    return bearer_token


def innkeeper_headers(bearer_token: str) -> dict:
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": bearer_token,
    }
    return headers


async def tenant_auth(test_client: AsyncClient, wallet_id: str, wallet_key: str) -> str:
    data = {"username": wallet_id, "password": wallet_key}
    token_resp = await test_client.post("/tenant/token", data=data)
    assert token_resp.status_code == 200, token_resp.content
    token_content = json.loads(token_resp.content)
    bearer_token = "Bearer " + token_content["access_token"]

    return bearer_token


def tenant_headers(bearer_token: str) -> dict:
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": bearer_token,
    }
    return headers
