import json
from behave import *
from starlette import status
from v1_api import *


@when('"{tenant}" sends "{contact_alias}" a message with content "{content}"')
def step_impl(context, tenant: str, contact_alias: str, content: str):
    # find recipient, get contact id
    contact = context.config.userdata[tenant]["connections"][contact_alias]

    response = send_message(context, tenant, contact["contact_id"], content)
    assert response.status_code == status.HTTP_200_OK, response.__dict__
    resp_json = json.loads(response.content)
    assert resp_json["item"]
    assert resp_json["item"]["content"] == content
    assert resp_json["item"]["contact"]["alias"] == contact_alias
    assert resp_json["item"]["role"] == "Sender"
    context.config.userdata[tenant].setdefault("messages", {})
    context.config.userdata[tenant]["messages"].setdefault(
        contact_alias, resp_json["item"]
    )

@then(
    '"{tenant}" can find {count:d} message(s) as "{role}" with "{contact_alias}" and tags "{tags}"'
)
def step_impl(
    context, tenant: str, count: int, role: str, contact_alias: str, tags: str
):
    contact = context.config.userdata[tenant]["connections"][contact_alias]

    params = {"role": role, "contact_id": contact["contact_id"], "tags": tags}
    response = list_messages(context, tenant, params)
    assert response.status_code == status.HTTP_200_OK, response.__dict__
    resp_json = json.loads(response.content)
    assert len(resp_json["items"]) == 1, resp_json
    assert resp_json["items"][0]["contact"]["alias"] == contact_alias
    _tags = [x.strip() for x in tags.split(",")]
    for t in _tags:
        assert t in resp_json["items"][0]["tags"]


@then('"{tenant}" can find {count:d} message(s) as "{role}" with "{contact_alias}"')
def step_impl(context, tenant: str, count: int, role: str, contact_alias: str):
    contact = context.config.userdata[tenant]["connections"][contact_alias]
    params = {"role": role, "contact_id": contact["contact_id"]}
    response = list_messages(context, tenant, params)
    assert response.status_code == status.HTTP_200_OK, response.__dict__
    resp_json = json.loads(response.content)
    assert len(resp_json["items"]) == 1, resp_json
    assert resp_json["items"][0]["contact"]["alias"] == contact_alias


@then('"{tenant}" can get message with "{contact_alias}" by message_id')
def step_impl(context, tenant: str, contact_alias: str):
    message = context.config.userdata[tenant]["messages"][contact_alias]
    response = get_message(context, tenant, message["message_id"])
    assert response.status_code == status.HTTP_200_OK, response.__dict__
    resp_json = json.loads(response.content)
    assert resp_json["item"]
    assert resp_json["item"]["contact"]["alias"] == contact_alias


@then('"{tenant}" can update message with "{contact_alias}"')
def step_impl(context, tenant: str, contact_alias: str):
    message = context.config.userdata[tenant]["messages"][contact_alias]
    payload = {"message_id": message["message_id"]}

    for row in context.table:
        attribute = row["attribute"]
        value = row["value"]
        if attribute == "tags":
            value = row["value"].split(",")

        payload[attribute] = value

    response = update_message(context, tenant, message["message_id"], payload)
    assert response.status_code == status.HTTP_200_OK, response.__dict__
    resp_json = json.loads(response.content)
    item = resp_json["item"]
    assert item["message_id"] == message["message_id"]
    for row in context.table:
        attribute = row["attribute"]
        value = row["value"]
        if attribute == "tags":
            value = row["value"].split(",")

        assert item[attribute] == value


@then('"{tenant}" can delete message with "{contact_alias}"')
def step_impl(context, tenant: str, contact_alias: str):
    message = context.config.userdata[tenant]["messages"][contact_alias]
    response = delete_message(context, tenant, message["message_id"])
    assert response.status_code == status.HTTP_200_OK, response.__dict__
    resp_json = json.loads(response.content)
    item = resp_json["item"]
    assert item["message_id"] == message["message_id"]
    assert item["deleted"]
    assert item["status"] == "Deleted"


@then('"{tenant}" cannot find message with "{contact_alias}" by role')
def step_impl(context, tenant: str, contact_alias: str):
    contact = context.config.userdata[tenant]["connections"][contact_alias]
    message = context.config.userdata[tenant]["messages"][contact_alias]
    params = {"contact_id": contact["contact_id"], "role": message["role"]}
    response = list_messages(context, tenant, params)
    assert response.status_code == status.HTTP_200_OK, response.__dict__
    resp_json = json.loads(response.content)
    assert len(resp_json["items"]) == 0, resp_json


@then('"{tenant}" can find message with "{contact_alias}" by role with deleted flag')
def step_impl(context, tenant: str, contact_alias: str):
    contact = context.config.userdata[tenant]["connections"][contact_alias]
    message = context.config.userdata[tenant]["messages"][contact_alias]
    params = {
        "contact_id": contact["contact_id"],
        "role": message["role"],
        "deleted": True,
    }
    response = list_messages(context, tenant, params)
    assert response.status_code == status.HTTP_200_OK, response.__dict__
    resp_json = json.loads(response.content)
    assert len(resp_json["items"]) == 1, resp_json
    assert resp_json["items"][0]["contact"]["alias"] == contact_alias
    assert resp_json["items"][0]["role"] == message["role"]
    assert resp_json["items"][0]["deleted"]
    assert resp_json["items"][0]["status"] == "Deleted"


@then('"{tenant}" cannot get message with "{contact_alias}"')
def step_impl(context, tenant: str, contact_alias: str):
    message = context.config.userdata[tenant]["messages"][contact_alias]
    response = get_message(context, tenant, message["message_id"])
    assert response.status_code == status.HTTP_404_NOT_FOUND, response.__dict__


@then('"{tenant}" can get message with "{contact_alias}" with deleted flag')
def step_impl(context, tenant: str, contact_alias: str):
    message = context.config.userdata[tenant]["messages"][contact_alias]
    params = {"deleted": True}
    response = get_message(context, tenant, message["message_id"], params)
    assert response.status_code == status.HTTP_200_OK, response.__dict__
    resp_json = json.loads(response.content)
    assert resp_json["item"]["contact"]["alias"] == contact_alias
    assert resp_json["item"]["deleted"]
    assert resp_json["item"]["status"] == "Deleted"
