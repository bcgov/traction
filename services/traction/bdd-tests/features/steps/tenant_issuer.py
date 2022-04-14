import json
import requests
import time
from behave import *
from starlette import status


@when('"{tenant}" registers as an issuer')
def step_impl(context, tenant: str):
    response = requests.post(
        context.config.userdata.get("traction_host") + "/tenant/v0/admin/issuer",
        headers=context.config.userdata[tenant]["auth_headers"],
    )
    assert response.status_code == status.HTTP_200_OK, response.__dict__
    resp_json = json.loads(response.content)
    # wait for ensdorser signatures and ledger writes
    time.sleep(2)
