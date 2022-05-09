import json
import requests

from behave import *
from starlette import status


# @then('"{holder}" will have a credential_offer from "{issuer}"')
# def step_impl(context, holder: str, issuer: str):
#     response = requests.post(
#         context.config.userdata.get("traction_host")
#         + "/tenant/v0/credentials/holder/offers",
#         headers=context.config.userdata[holder]["auth_headers"],
#     )
#     assert response.status_code == status.HTTP_200_OK, response.__dict__

#     assert False, json.loads(response.content)
