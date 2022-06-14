from email.base64mime import body_decode
import json, requests
from behave import *
from sqlalchemy import false
from starlette import status
from v1_api import *
from pprint import pp


@step('"{verifier}" requests proof of keys in schema "{schema_name}" from "{prover}"')
def step_impl(context, verifier: str, schema_name: str, prover: str):
    # verifier is also assumed to be issuer
    body = {
        "contact_id": context.config.userdata[verifier]["connections"][prover][
            "contact_id"
        ],
        "proof_request": {
            "requested_attributes": [
                {
                    "names": context.config.userdata[verifier][schema_name][
                        "schema_template"
                    ]["attributes"],
                    "restrictions": [
                        {
                            "cred_def_id": context.config.userdata[verifier][
                                schema_name
                            ]["credential_template"]["cred_def_id"]
                        }
                    ],
                }
            ],
            "requested_predicates": [],
            "non_revoked": {},
        },
    }
    response = requests.post(
        context.config.userdata.get("traction_host")
        + "/tenant/v1/verifier/presentation_requests/v1/",
        json=body,
        headers=context.config.userdata[verifier]["auth_headers"],
    )

    assert response.status_code == status.HTTP_201_CREATED, response.__dict__
    resp_json = json.loads(response.content)
    assert resp_json["item"]["status"] == "pending"
