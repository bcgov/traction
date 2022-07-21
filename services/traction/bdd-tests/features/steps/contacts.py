import json
import pprint
from pprint import pp

from behave import *
from starlette import status
from v1_api import *


@when('"{tenant}" creates invitation(s)')
def step_impl(context, tenant: str):
    for row in context.table:
        alias = row["alias"]
        invitation_type = row["invitation_type"]

        response = create_invitation(context, tenant, alias, invitation_type)
        assert response.status_code == status.HTTP_200_OK, response.__dict__
        resp_json = json.loads(response.content)
        assert resp_json["item"]
        assert resp_json["invitation"]
        assert resp_json["invitation_url"]
        response.status_code == status.HTTP_200_OK, resp_json
        context.config.userdata[tenant].setdefault("contacts", {})
        context.config.userdata[tenant]["contacts"].setdefault(alias, resp_json["item"])


@then('"{tenant}" will have {count:d} contact(s)')
def step_impl(context, tenant: str, count: int):
    params = {}
    response = list_contacts(context, tenant, params)
    assert response.status_code == status.HTTP_200_OK, response.__dict__
    resp_json = json.loads(response.content)
    assert resp_json["total"] == count, resp_json


@then('"{tenant}" can find contact "{contact}" by alias')
def step_impl(context, tenant: str, contact: str):
    params = {"alias": contact}
    response = list_contacts(context, tenant, params)
    assert response.status_code == status.HTTP_200_OK, response.__dict__
    resp_json = json.loads(response.content)
    assert len(resp_json["items"]) == 1, resp_json
    assert resp_json["items"][0]["alias"] == contact


@then('"{tenant}" can find contact "{contact}" by tags "{tags}"')
def step_impl(context, tenant: str, contact: str, tags: str):
    params = {"tags": tags, "alias": contact}
    response = list_contacts(context, tenant, params)
    assert response.status_code == status.HTTP_200_OK, response.__dict__
    resp_json = json.loads(response.content)
    assert len(resp_json["items"]) == 1, resp_json
    assert resp_json["items"][0]["alias"] == contact
    _tags = [x.strip() for x in tags.split(",")]
    for t in _tags:
        assert t in resp_json["items"][0]["tags"]


@then('"{tenant}" cannot find contact "{contact}" by alias')
def step_impl(context, tenant: str, contact: str):
    params = {"alias": contact}
    response = list_contacts(context, tenant, params)
    assert response.status_code == status.HTTP_200_OK, response.__dict__
    resp_json = json.loads(response.content)
    assert len(resp_json["items"]) == 0, resp_json


@then('"{tenant}" can find contact "{contact}" with deleted flag')
def step_impl(context, tenant: str, contact: str):
    params = {"alias": contact, "deleted": True}
    response = list_contacts(context, tenant, params)
    assert response.status_code == status.HTTP_200_OK, response.__dict__
    resp_json = json.loads(response.content)
    assert len(resp_json["items"]) == 1, resp_json
    assert resp_json["items"][0]["alias"] == contact
    assert resp_json["items"][0]["deleted"]
    assert resp_json["items"][0]["status"] == "Deleted"


@then('"{tenant}" can get contact "{contact_alias}" by contact_id')
def step_impl(context, tenant: str, contact_alias: str):
    contact = context.config.userdata[tenant]["contacts"][contact_alias]
    response = get_contact(context, tenant, contact["contact_id"])
    assert response.status_code == status.HTTP_200_OK, response.__dict__
    resp_json = json.loads(response.content)
    assert resp_json["item"]["contact_id"] == contact["contact_id"]
    pp(resp_json)


@then('"{tenant}" can get contact "{contact_alias}" with timeline')
def step_impl(context, tenant: str, contact_alias: str):
    contact = context.config.userdata[tenant]["contacts"][contact_alias]
    params = {"timeline": True}
    response = get_contact(context, tenant, contact["contact_id"], params)
    assert response.status_code == status.HTTP_200_OK, response.__dict__
    resp_json = json.loads(response.content)
    assert resp_json["item"]["contact_id"] == contact["contact_id"]
    assert len(resp_json["timeline"]) > 0


@then('"{tenant}" can get contact "{contact_alias}" with acapy')
def step_impl(context, tenant: str, contact_alias: str):
    contact = context.config.userdata[tenant]["contacts"][contact_alias]
    params = {"acapy": True}
    response = get_contact(context, tenant, contact["contact_id"], params)
    assert response.status_code == status.HTTP_200_OK, response.__dict__
    resp_json = json.loads(response.content)
    assert resp_json["item"]["contact_id"] == contact["contact_id"]
    assert resp_json["item"]["acapy"] is not None
    assert resp_json["item"]["acapy"]["connection"] is not None
    assert resp_json["item"]["acapy"]["connection"]["connection_id"] is not None
    pp(resp_json)


@then('"{tenant}" cannot get contact "{contact_alias}" by contact_id')
def step_impl(context, tenant: str, contact_alias: str):
    contact = context.config.userdata[tenant]["contacts"][contact_alias]
    response = get_contact(context, tenant, contact["contact_id"])
    assert response.status_code == status.HTTP_404_NOT_FOUND, response.__dict__


@then('"{tenant}" can get contact "{contact_alias}" with deleted flag')
def step_impl(context, tenant: str, contact_alias: str):
    contact = context.config.userdata[tenant]["contacts"][contact_alias]
    params = {"deleted": True}
    response = get_contact(context, tenant, contact["contact_id"], params)
    assert response.status_code == status.HTTP_200_OK, response.__dict__
    resp_json = json.loads(response.content)
    assert resp_json["item"]["contact_id"] == contact["contact_id"]
    assert resp_json["item"]["deleted"]
    assert resp_json["item"]["status"] == "Deleted"


@then('"{tenant}" will have a next page link in contact list')
def step_impl(context, tenant: str):
    params = {}
    response = list_contacts(context, tenant, params)
    assert response.status_code == status.HTTP_200_OK, response.__dict__
    resp_json = json.loads(response.content)
    assert len(resp_json["items"]) == 10, resp_json
    assert len(resp_json["links"]) > 0
    found_rel_next = False
    for link in resp_json["links"]:
        found_rel_next = link["rel"] == "next"

    assert found_rel_next


@then('"{tenant}" can update contact "{contact_alias}"')
def step_impl(context, tenant: str, contact_alias: str):
    contact = context.config.userdata[tenant]["contacts"][contact_alias]
    payload = {"contact_id": contact["contact_id"]}

    for row in context.table:
        attribute = row["attribute"]
        value = row["value"]
        if attribute == "tags":
            value = row["value"].split(",")

        payload[attribute] = value

    response = update_contact(context, tenant, contact["contact_id"], payload)
    assert response.status_code == status.HTTP_200_OK, response.__dict__
    resp_json = json.loads(response.content)
    item = resp_json["item"]
    assert item["contact_id"] == contact["contact_id"]
    for row in context.table:
        attribute = row["attribute"]
        value = row["value"]
        if attribute == "tags":
            value = row["value"].split(",")

        assert item[attribute] == value


@then('"{tenant}" can delete contact "{contact_alias}"')
def step_impl(context, tenant: str, contact_alias: str):
    contact = context.config.userdata[tenant]["contacts"][contact_alias]
    response = delete_contact(context, tenant, contact["contact_id"])
    assert response.status_code == status.HTTP_200_OK, response.__dict__
    resp_json = json.loads(response.content)
    item = resp_json["item"]
    assert item["contact_id"] == contact["contact_id"]
    assert item["deleted"]
    assert item["status"] == "Deleted"


@step('"{tenant_1}" and "{tenant_2}" cannot read each others contacts')
def step_impl(context, tenant_1: str, tenant_2: str):
    for row in context.table:
        if row["tenant"] == tenant_1:
            contact_1_alias = row["alias"]
        elif row["tenant"] == tenant_2:
            contact_2_alias = row["alias"]

    params = {}

    # can list their own
    response = list_contacts(context, tenant_1, params)
    assert response.status_code == status.HTTP_200_OK, response.__dict__
    resp_json = json.loads(response.content)
    assert resp_json["total"] == 1, resp_json
    contact_1 = resp_json["items"][0]
    # expected alias
    assert contact_1["alias"] == contact_1_alias, resp_json

    response = list_contacts(context, tenant_2, params)
    assert response.status_code == status.HTTP_200_OK, response.__dict__
    resp_json = json.loads(response.content)
    contact_2 = resp_json["items"][0]
    # expected alias
    assert contact_2["alias"] == contact_2_alias, resp_json

    # contacts are different
    assert contact_1["contact_id"] != contact_2["contact_id"]

    # can get their own
    response = get_contact(context, tenant_1, contact_1["contact_id"])
    assert response.status_code == status.HTTP_200_OK, response.__dict__

    response = get_contact(context, tenant_2, contact_2["contact_id"])
    assert response.status_code == status.HTTP_200_OK, response.__dict__

    # cannot get the others
    response = get_contact(context, tenant_1, contact_2["contact_id"])
    assert response.status_code == status.HTTP_404_NOT_FOUND, response.__dict__

    response = get_contact(context, tenant_2, contact_1["contact_id"])
    assert response.status_code == status.HTTP_404_NOT_FOUND, response.__dict__
