import json

import pytest

from httpx import AsyncClient

from api.endpoints.models.v1.contacts import CreateInvitationResponse
from tests.integration.endpoints.routes.test_tenant_utils import create_tenant
from tests.test_utils import (
    innkeeper_auth,
    innkeeper_headers,
)

pytestmark = pytest.mark.asyncio


@pytest.mark.integtest
async def test_contacts_create_invitation(app_client: AsyncClient) -> None:
    # get a token
    bearer_token = await innkeeper_auth(app_client)
    ik_headers = innkeeper_headers(bearer_token)

    t1_headers = await create_tenant(
        app_client,
        ik_headers,
        tenant_name="test_contacts_create_invitation",
        make_issuer=False,
    )

    alias = "test_contacts_create_invitation_invitee"

    data = {"alias": alias, "invitation_type": "didexchange/1.0"}
    resp_invitation = await app_client.post(
        "/tenant/v1/contacts/create-invitation", json=data, headers=t1_headers
    )
    assert resp_invitation.status_code == 200, resp_invitation.content

    resp = CreateInvitationResponse(**json.loads(resp_invitation.content))
    assert resp.item, resp.item.alias == alias
