import pprint

from behave import *
from v1_api import *


def assert_deprecated(response):
    assert response.status_code == status.HTTP_410_GONE, response.__dict__
    assert response.headers.get("sunset"), response.headers
    assert response.headers.get("deprecated"), response.headers
    pprint.pp(response.__dict__)


@step('"{tenant}" sends "{contact_alias}" a message with content "{content}"')
def step_impl(context, tenant: str, contact_alias: str, content: str):
    # find recipient, get contact id
    contact = context.config.userdata[tenant]["connections"][contact_alias]

    response = send_message(context, tenant, contact["contact_id"], content)
    assert_deprecated(response)


@then(
    '"{tenant}" can find {count:d} message(s) as "{role}" with "{contact_alias}" and tags "{tags}"'
)
def step_impl(
    context, tenant: str, count: int, role: str, contact_alias: str, tags: str
):
    contact = context.config.userdata[tenant]["connections"][contact_alias]

    params = {"role": role, "contact_id": contact["contact_id"], "tags": tags}
    response = list_messages(context, tenant, params)
    assert_deprecated(response)


@then('"{tenant}" can find {count:d} message(s) as "{role}" with "{contact_alias}"')
def step_impl(context, tenant: str, count: int, role: str, contact_alias: str):
    contact = context.config.userdata[tenant]["connections"][contact_alias]
    params = {"role": role, "contact_id": contact["contact_id"]}
    response = list_messages(context, tenant, params)
    assert_deprecated(response)


@then('"{tenant}" can get message with "{contact_alias}" by message_id')
def step_impl(context, tenant: str, contact_alias: str):
    message = context.config.userdata[tenant]["messages"][contact_alias]
    response = get_message(context, tenant, message["message_id"])
    assert_deprecated(response)


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
    assert_deprecated(response)


@then('"{tenant}" can delete message with "{contact_alias}"')
def step_impl(context, tenant: str, contact_alias: str):
    message = context.config.userdata[tenant]["messages"][contact_alias]
    response = delete_message(context, tenant, message["message_id"])
    assert_deprecated(response)


@then('"{tenant}" cannot find message with "{contact_alias}" by role')
def step_impl(context, tenant: str, contact_alias: str):
    contact = context.config.userdata[tenant]["connections"][contact_alias]
    message = context.config.userdata[tenant]["messages"][contact_alias]
    params = {"contact_id": contact["contact_id"], "role": message["role"]}
    response = list_messages(context, tenant, params)
    assert_deprecated(response)


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
    assert_deprecated(response)


@then('"{tenant}" cannot get message with "{contact_alias}"')
def step_impl(context, tenant: str, contact_alias: str):
    message = context.config.userdata[tenant]["messages"][contact_alias]
    response = get_message(context, tenant, message["message_id"])
    assert_deprecated(response)


@then('"{tenant}" can get message with "{contact_alias}" with deleted flag')
def step_impl(context, tenant: str, contact_alias: str):
    message = context.config.userdata[tenant]["messages"][contact_alias]
    params = {"deleted": True}
    response = get_message(context, tenant, message["message_id"], params)
    assert_deprecated(response)


@step('"{tenant}" sets configuration "{configuration_name}" to "{flag:bool}"')
def step_impl(context, tenant: str, configuration_name: str, flag: bool):
    payload = {configuration_name: flag}
    response = tenant_update_configuration(context, tenant, payload)
    resp_json = json.loads(response.content)
    assert resp_json["item"][configuration_name] == flag


@step('"{tenant}" messages as "{role}" have no content')
def step_impl(context, tenant: str, role: str):
    params = {"role": role}
    response = list_messages(context, tenant, params)
    assert_deprecated(response)


@step('"{tenant}" messages as "{role}" will have content')
def step_impl(context, tenant: str, role: str):
    params = {"role": role}
    response = list_messages(context, tenant, params)
    assert_deprecated(response)
