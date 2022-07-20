import json, requests
from pprint import pp
from behave import *
from starlette import status


@step('"{verifier}" requests proof of keys in schema "{schema_name}" from "{prover}"')
def step_impl(context, verifier: str, schema_name: str, prover: str):
    # verifier is also assumed to be issuer
    body = {
        "contact_id": context.config.userdata[verifier]["connections"][prover][
            "contact_id"
        ],
        "name": schema_name,
        "version": "1.0.0",
        "comment": "asking for BDD test",
        "external_reference_id": "bdd-test-1",
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
        + "/tenant/v1/verifier/presentations/adhoc-request",
        json=body,
        headers=context.config.userdata[verifier]["auth_headers"],
    )
    assert response.status_code == status.HTTP_200_OK, response.__dict__
    resp_json = json.loads(response.content)
    assert resp_json["item"]["status"] == "pending"

    # update presentation_requests list
    context.config.userdata[verifier].setdefault(
        "verifier_presentations", [resp_json["item"]]
    )


@step('"{verifier}" has a "{status_code}" verifier presentation')
def step_impl(context, verifier: str, status_code: str):

    response = requests.get(
        context.config.userdata.get("traction_host")
        + "/tenant/v1/verifier/presentations/",
        headers=context.config.userdata[verifier]["auth_headers"],
    )

    assert response.status_code == status.HTTP_200_OK, response.__dict__
    resp_json = json.loads(response.content)
    assert resp_json["items"][0]["status"] == status_code, resp_json["items"]

    verifier_presentation_id = resp_json["items"][0]["verifier_presentation_id"]

    response = requests.get(
        context.config.userdata.get("traction_host")
        + f"/tenant/v1/verifier/presentations/{verifier_presentation_id}?acapy=true",
        headers=context.config.userdata[verifier]["auth_headers"],
    )
    assert response.status_code == status.HTTP_200_OK, response.__dict__
    resp_json = json.loads(response.content)
    pp(resp_json)
