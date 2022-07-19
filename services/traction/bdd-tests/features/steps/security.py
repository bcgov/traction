import requests
import json

from behave import *
from starlette import status


@then(
    '"{tenant_1}" cannot NOT get "{tenant_2}"s contact to "{tenant_2_contact_alias}" by id'
)
def step_impl(context, tenant_1: str, tenant_2: str, tenant_2_contact_alias: str):

    response1 = requests.get(
        context.config.userdata.get("traction_host") + "/tenant/v1/contacts",
        params={"alias": tenant_2_contact_alias},
        headers=context.config.userdata[tenant_2]["auth_headers"],
    )
    assert response1.status_code == status.HTTP_200_OK, response1.__dict__
    tenant_2_contact = json.loads(response1.content)["items"][0]

    response2 = requests.get(
        context.config.userdata.get("traction_host")
        + f"/tenant/v1/contacts/{tenant_2_contact['contact_id']}",
        headers=context.config.userdata[tenant_1]["auth_headers"],
    )
    assert response2.status_code == status.HTTP_404_NOT_FOUND, response2.__dict__
