import requests
import json

from behave import *
from starlette import status
from v1_api import *


@then(
    '"{tenant_1}" can NOT get "{tenant_2}"s contact to "{tenant_2_contact_alias}" by id'
)
def step_impl(context, tenant_1: str, tenant_2: str, tenant_2_contact_alias: str):

    response1 = list_contacts(context, tenant_2, {"alias": tenant_2_contact_alias})
    assert response1.status_code == status.HTTP_200_OK, response1.__dict__
    tenant_2_contact = json.loads(response1.content)["items"][0]

    response2 = get_contact(context, tenant_1, tenant_2_contact["contact_id"])
    assert response2.status_code == status.HTTP_404_NOT_FOUND, response2.__dict__
