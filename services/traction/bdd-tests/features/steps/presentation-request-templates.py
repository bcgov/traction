import json
import pprint

from behave import *
from starlette import status

from v1_api import *


@step('"{tenant}" creates presentation request template for "{schema_name}"')
def step_impl(context, tenant: str, schema_name: str):
    context.config.userdata[tenant].setdefault("presentation_request_templates", {})

    for row in context.table:
        # | name | external_reference_id | tags |
        name = row["name"]
        external_reference_id = row["external_reference_id"]
        tags = row["tags"].split(",")

        payload = {
            "name": name,
            "external_reference_id": external_reference_id,
            "tags": tags,
            "presentation_request": {
                "requested_attributes": [
                    {
                        "names": context.config.userdata[tenant][schema_name][
                            "schema_template"
                        ]["attributes"],
                        "restrictions": [
                            {
                                "cred_def_id": context.config.userdata[tenant][
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

        response = create_presentation_request_template(context, tenant, payload)
        assert response.status_code == status.HTTP_200_OK, response.__dict__
        resp_json = json.loads(response.content)
        pprint.pp(resp_json)
        assert resp_json["item"] is not None, resp_json
        assert resp_json["item"]["name"] == row["name"], name
        assert (
            resp_json["item"]["external_reference_id"] == external_reference_id
        ), resp_json
        assert resp_json["item"]["tags"] == tags, resp_json
        context.config.userdata[tenant]["presentation_request_templates"][
            resp_json["item"]["name"]
        ] = resp_json["item"]


@step('"{tenant}" will have {count:d} presentation request template(s)')
def step_impl(context, tenant: str, count: int):
    params = {}
    response = list_presentation_request_templates(context, tenant, params)
    assert response.status_code == status.HTTP_200_OK, response.__dict__
    resp_json = json.loads(response.content)
    assert resp_json["total"] == count, resp_json
    # reset the stored presentation_request_templates
    context.config.userdata[tenant].setdefault("presentation_request_templates", {})
    for item in resp_json["items"]:
        context.config.userdata[tenant]["presentation_request_templates"][
            item["name"]
        ] = item


@step('"{tenant}" will reload presentation request template(s)')
def step_impl(context, tenant: str):
    params = {}
    response = list_presentation_request_templates(context, tenant, params)
    assert response.status_code == status.HTTP_200_OK, response.__dict__
    resp_json = json.loads(response.content)
    # reset the stored presentation_request_templates
    context.config.userdata[tenant].setdefault("presentation_request_templates", {})
    for item in resp_json["items"]:
        context.config.userdata[tenant]["presentation_request_templates"][
            item["name"]
        ] = item


@then('"{tenant}" can update presentation request template "{template_name}"')
def step_impl(context, tenant: str, template_name: str):
    _template = context.config.userdata[tenant]["presentation_request_templates"][
        template_name
    ]

    payload = {
        "presentation_request_template_id": _template[
            "presentation_request_template_id"
        ]
    }

    for row in context.table:
        attribute = row["attribute"]
        value = row["value"]
        if attribute == "tags":
            value = row["value"].split(",")

        payload[attribute] = value

    response = update_presentation_request_template(
        context, tenant, _template["presentation_request_template_id"], payload
    )
    assert response.status_code == status.HTTP_200_OK, response.__dict__
    resp_json = json.loads(response.content)
    item = resp_json["item"]
    assert (
        item["presentation_request_template_id"]
        == _template["presentation_request_template_id"]
    )
    for row in context.table:
        attribute = row["attribute"]
        value = row["value"]
        if attribute == "tags":
            value = row["value"].split(",")

        assert item[attribute] == value


@then(
    '"{tenant}" requests proof of keys with template "{template_name}" from "{holder}"'
)
def step_impl(context, tenant: str, template_name: str, holder: str):
    _template = context.config.userdata[tenant]["presentation_request_templates"][
        template_name
    ]
    contact_id = context.config.userdata[tenant]["connections"][holder]["contact_id"]

    payload = {
        "contact_id": contact_id,
        "version": "1.0.0",
        "comment": "asking for BDD test",
        "external_reference_id": "bdd-test-1",
        "presentation_request_template_id": _template[
            "presentation_request_template_id"
        ],
    }
    response = send_request_from_presentation_request_template(
        context, tenant, _template["presentation_request_template_id"], payload
    )
    assert response.status_code == status.HTTP_200_OK, response.__dict__
    resp_json = json.loads(response.content)
    assert resp_json["item"]["status"] == "pending"


@step('"{tenant}" can find presentation request template by tags "{tags}"')
def step_impl(context, tenant: str, tags: str):
    params = {"tags": tags}
    response = list_presentation_request_templates(context, tenant, params)
    assert response.status_code == status.HTTP_200_OK, response.__dict__
    resp_json = json.loads(response.content)
    assert len(resp_json["items"]) == 1, resp_json
    _tags = [x.strip() for x in tags.split(",")]
    for t in _tags:
        assert t in resp_json["items"][0]["tags"]


@step(
    '"{tenant}" can find presentation request template by external reference id "{ref_id}"'
)
def step_impl(context, tenant: str, ref_id: str):
    params = {"external_reference_id": ref_id}
    response = list_presentation_request_templates(context, tenant, params)
    assert response.status_code == status.HTTP_200_OK, response.__dict__
    resp_json = json.loads(response.content)
    assert len(resp_json["items"]) == 1, resp_json
    assert resp_json["items"][0]["external_reference_id"] == ref_id, resp_json


@step('"{tenant}" can get presentation request template "{template_name}" by id')
def step_impl(context, tenant: str, template_name: str):
    _template = context.config.userdata[tenant]["presentation_request_templates"][
        template_name
    ]
    item_id = _template["presentation_request_template_id"]
    params = {}
    response = get_presentation_request_template(context, tenant, item_id, params)
    assert response.status_code == status.HTTP_200_OK, response.__dict__
    resp_json = json.loads(response.content)
    assert resp_json["item"]["presentation_request_template_id"] == item_id, resp_json


@then('"{tenant}" can delete presentation request template "{template_name}"')
def step_impl(context, tenant: str, template_name: str):
    _template = context.config.userdata[tenant]["presentation_request_templates"][
        template_name
    ]
    item_id = _template["presentation_request_template_id"]
    response = delete_presentation_request_template(context, tenant, item_id)
    assert response.status_code == status.HTTP_200_OK, response.__dict__
    resp_json = json.loads(response.content)
    assert resp_json["item"]["presentation_request_template_id"] == item_id, resp_json
    assert resp_json["item"]["deleted"], resp_json
    assert resp_json["item"]["status"] == "Deleted", resp_json


@step('"{tenant}" cannot find presentation request template by tags "{tags}"')
def step_impl(context, tenant: str, tags: str):
    params = {"tags": tags}
    response = list_presentation_request_templates(context, tenant, params)
    assert response.status_code == status.HTTP_200_OK, response.__dict__
    resp_json = json.loads(response.content)
    assert len(resp_json["items"]) == 0, resp_json


@step(
    '"{tenant}" cannot find presentation request template by external reference id "{ref_id}"'
)
def step_impl(context, tenant: str, ref_id: str):
    params = {"external_reference_id": ref_id}
    response = list_presentation_request_templates(context, tenant, params)
    assert response.status_code == status.HTTP_200_OK, response.__dict__
    resp_json = json.loads(response.content)
    assert len(resp_json["items"]) == 0, resp_json


@step('"{tenant}" cannot get presentation request template "{template_name}" by id')
def step_impl(context, tenant: str, template_name: str):
    _template = context.config.userdata[tenant]["presentation_request_templates"][
        template_name
    ]
    item_id = _template["presentation_request_template_id"]
    params = {}
    response = get_presentation_request_template(context, tenant, item_id, params)
    assert response.status_code == status.HTTP_404_NOT_FOUND, response.__dict__


@step(
    '"{tenant}" can get presentation request template "{template_name}" by id and deleted flag'
)
def step_impl(context, tenant: str, template_name: str):
    _template = context.config.userdata[tenant]["presentation_request_templates"][
        template_name
    ]
    item_id = _template["presentation_request_template_id"]
    params = {"deleted": True}
    response = get_presentation_request_template(context, tenant, item_id, params)
    assert response.status_code == status.HTTP_200_OK, response.__dict__
    resp_json = json.loads(response.content)
    assert resp_json["item"]["presentation_request_template_id"] == item_id, resp_json
    assert resp_json["item"]["deleted"], resp_json
    assert resp_json["item"]["status"] == "Deleted", resp_json


@step(
    '"{tenant}" can find presentation request template "{template_name}" by tags "{tags}" and deleted flag'
)
def step_impl(context, tenant: str, template_name: str, tags: str):
    _template = context.config.userdata[tenant]["presentation_request_templates"][
        template_name
    ]
    item_id = _template["presentation_request_template_id"]
    params = {"tags": tags, "deleted": True}
    response = list_presentation_request_templates(context, tenant, params)
    assert response.status_code == status.HTTP_200_OK, response.__dict__
    resp_json = json.loads(response.content)
    assert len(resp_json["items"]) == 1, resp_json
    item = resp_json["items"][0]
    assert item["presentation_request_template_id"] == item_id, resp_json
    assert item["deleted"], resp_json
    assert item["status"] == "Deleted", resp_json
    _tags = [x.strip() for x in tags.split(",")]
    for t in _tags:
        assert t in item["tags"]
