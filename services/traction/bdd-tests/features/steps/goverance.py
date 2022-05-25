import json
import requests
import time

from behave import *
from starlette import status


@given(
    '"{issuer}" writes a new schema "{schema_name}" and cred def tagged "{cred_def_tag}"'
)
@when(
    '"{issuer}" writes a new schema "{schema_name}" and cred def tagged "{cred_def_tag}"'
)
def step_impl(context, issuer: str, schema_name: str, cred_def_tag: str):

    payload = {
          "schema_definition": {
            "schema_name": schema_name,
            "schema_version": "0.1",
            "attributes": [row["attr"] for row in context.table]
          },
         "name": schema_name,
         "tags": [],
          "credential_definition": {
            "tag": cred_def_tag,
            "revocation_enabled": False,
            "revocation_registry_size": 0
          }
        }

    response = requests.post(
        context.config.userdata.get("traction_host") + "/tenant/v1/governance/schema_templates/",
        json=payload,
        headers=context.config.userdata[issuer]["auth_headers"],
    )
    resp_json = json.loads(response.content)
    # {
    #   "item": {
    #     "status": "Pending",
    #     "state": "init",
    #     "deleted": false,
    #     "created_at": "2022-05-25T19:45:20.099576",
    #     "updated_at": "2022-05-25T19:45:20.099576",
    #     "tags": [],
    #     "schema_template_id": "4e4d88b6-dda5-493c-a0ed-90ffd380fde1",
    #     "tenant_id": "42695695-5709-49c5-9c41-609b1044ce80",
    #     "schema_id": "TRn8mjJDfK8ukkvVrVgXMJ:2:useless-schema:0.1",
    #     "name": "useless-schema",
    #     "imported": false,
    #     "schema_name": "useless-schema",
    #     "version": "0.1",
    #     "attributes": [
    #       "name",
    #       "title"
    #     ]
    #   },
    #   "links": [],
    #   "credential_template": {
    #     "status": "Pending",
    #     "state": "init",
    #     "deleted": false,
    #     "created_at": "2022-05-25T19:45:20.099576",
    #     "updated_at": "2022-05-25T19:45:20.099576",
    #     "tags": [],
    #     "schema_template_id": "4e4d88b6-dda5-493c-a0ed-90ffd380fde1",
    #     "credential_template_id": "ef020cf8-be7b-43ff-a506-e00528f21896",
    #     "tenant_id": "42695695-5709-49c5-9c41-609b1044ce80",
    #     "schema_id": "TRn8mjJDfK8ukkvVrVgXMJ:2:useless-schema:0.1",
    #     "cred_def_id": null,
    #     "name": "useless-schema",
    #     "revocation_enabled": false,
    #     "attributes": [
    #       "name",
    #       "title"
    #     ],
    #     "tag": "test"
    #   }
    # }
    # while we are here, update context.governance
    context.config.userdata.setdefault("schema_template", resp_json["item"])
    context.config.userdata.setdefault("credential_template", resp_json["credential_template"])

    assert response.status_code == status.HTTP_200_OK, response.__dict__


@given(
    'check "{tenant}" for {timeout} seconds for a cred_def status of "{cred_def_state}" for "{schema_name}"'
)
@then(
    'check "{tenant}" for {timeout} seconds for a cred_def status of "{cred_def_state}" for "{schema_name}"'
)
def step_impl(
    context,
    tenant: str,
    timeout: str,  # don't know how to make an int natively
    cred_def_state: str,
    schema_name: str,
):
    ex_result_found = False
    timeout = int(timeout)
    check_period = (
        float(timeout / 20) if timeout > 20 else 1
    )  # only check maximum of 20 times
    time_passed = 0
    attempts = 0
    limit = 20
    while attempts < limit:
        limit = limit + 1
        time.sleep(float(10))

        response_data = get_credential_template(
            context, tenant
        )
        ex_result_found = response_data["state"] == cred_def_state
        if ex_result_found:
            break

    assert (
        ex_result_found
    ), f"after {timeout} seconds, tenant_schema found was {response_data}"

    # while we are here, update context.governance
    # context.config.userdata.setdefault("governance", {})

    # context.config.userdata["governance"]["schemas"] = {
    #     i["schema_name"]: i for i in response_data["items"]
    # }
    print(f"Polled for {tenant} seconds")


# @given(
#     '"{tenant}" has a tenant_schema record with a cred_def status of "{cred_def_state}" for "{schema_name}"'
# )
# @then(
#     '"{tenant}" will have a tenant_schema record with a cred_def status of "{cred_def_state}" for "{schema_name}"'
# )
def get_governance_schemas(context, tenant: str, cred_def_state: str, schema_name: str):

    response = requests.get(
        context.config.userdata.get("traction_host") + "/tenant/v1/governance/schema_templates",
        headers=context.config.userdata[tenant]["auth_headers"],
    )
    assert response.status_code == status.HTTP_200_OK, response.__dict__

    content = json.loads(response.content)

    assert len(content["items"]) > 0, content
    return content


def get_credential_template(context, tenant: str):

    credential_template_id = context.config.userdata["credential_template"]["credential_template_id"]
    response = requests.get(
        context.config.userdata.get("traction_host") + f"/tenant/v1/governance/credential_templates/{credential_template_id}",
        headers=context.config.userdata[tenant]["auth_headers"],
    )
    assert response.status_code == status.HTTP_200_OK, response.__dict__

    content = json.loads(response.content)

    assert content["item"] is not None
    context.config.userdata["credential_template"] = content["item"]
    return content["item"]