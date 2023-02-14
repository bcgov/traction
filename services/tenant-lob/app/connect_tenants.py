import requests

from utils import wait_a_bit
from config import PROXY_URL


async def connect_tenants(inviter, invitee):
    inviter_headers = {"Authorization": f"Bearer {inviter['token']}"}
    inviter_name = inviter["tenant"]["tenant_name"]

    invitee_headers = {"Authorization": f"Bearer {invitee['token']}"}
    invitee_name = invitee["tenant"]["tenant_name"]

    # create an invitation
    data = {"my_label": inviter_name}
    params = {
        "alias": invitee_name,
        "auto_accept": "true",
    }
    res = requests.post(
        f"{PROXY_URL}/connections/create-invitation",
        headers=inviter_headers,
        json=data,
        params=params,
    )
    invitation = res.json()["invitation"]
    inviter_connection_id = res.json()["connection_id"]
    # invitation_url = res.json()["invitation_url"]

    # out of band, this invitation would be delivered to invitee
    # maybe a qr code is generated from the invitation_url for the invitee to scan...

    # invitee accepts the invitation
    data = invitation
    params = {
        "alias": inviter_name,
        "auto_accept": "true",
    }
    res = requests.post(
        f"{PROXY_URL}/connections/receive-invitation",
        headers=invitee_headers,
        json=data,
        params=params,
    )
    invitee_connection_id = res.json()["connection_id"]

    # let it run a bit as the auto accept works...
    wait_a_bit(3)

    res = requests.get(
        f"{PROXY_URL}/connections/{inviter_connection_id}",
        headers=inviter_headers,
    )
    connection_1 = res.json()
    print(connection_1)

    res = requests.get(
        f"{PROXY_URL}/connections/{invitee_connection_id}",
        headers=invitee_headers,
    )
    connection_2 = res.json()
    print(connection_2)

    return {
        "inviter": inviter_name,
        "invitee": invitee_name,
        "inviter_connection": connection_1,
        "invitee_connection": connection_2,
    }
