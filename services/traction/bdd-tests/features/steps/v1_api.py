import requests


def create_invitation(context, tenant, alias, invitation_type):
    data = {"alias": alias, "invitation_type": invitation_type}
    response = requests.post(
        context.config.userdata.get("traction_host")
        + "/tenant/v1/contacts/create-invitation",
        json=data,
        headers=context.config.userdata[tenant]["auth_headers"],
    )
    return response


def list_contacts(context, tenant, params):
    response = requests.get(
        context.config.userdata.get("traction_host") + "/tenant/v1/contacts",
        params=params,
        headers=context.config.userdata[tenant]["auth_headers"],
    )
    return response


def get_contact(context, tenant, contact_id, params: dict | None = {}):
    response = requests.get(
        context.config.userdata.get("traction_host")
        + f"/tenant/v1/contacts/{contact_id}",
        params=params,
        headers=context.config.userdata[tenant]["auth_headers"],
    )
    return response


def update_contact(context, tenant, contact_id, payload):
    response = requests.put(
        context.config.userdata.get("traction_host")
        + f"/tenant/v1/contacts/{contact_id}",
        json=payload,
        headers=context.config.userdata[tenant]["auth_headers"],
    )
    return response


def delete_contact(context, tenant, contact_id):
    response = requests.delete(
        context.config.userdata.get("traction_host")
        + f"/tenant/v1/contacts/{contact_id}",
        headers=context.config.userdata[tenant]["auth_headers"],
    )
    return response


def create_schema_template(context, tenant, payload):
    response = requests.post(
        context.config.userdata.get("traction_host")
        + "/tenant/v1/governance/schema_templates/",
        json=payload,
        headers=context.config.userdata[tenant]["auth_headers"],
    )
    return response


def list_schema_templates(context, tenant, params):
    response = requests.get(
        context.config.userdata.get("traction_host")
        + "/tenant/v1/governance/schema_templates",
        params=params,
        headers=context.config.userdata[tenant]["auth_headers"],
    )
    return response


def list_credential_templates(context, tenant, params):
    response = requests.get(
        context.config.userdata.get("traction_host")
        + "/tenant/v1/governance/credential_templates",
        params=params,
        headers=context.config.userdata[tenant]["auth_headers"],
    )
    return response


def get_schema_template(context, tenant, item_id, params: dict | None = {}):
    response = requests.get(
        context.config.userdata.get("traction_host")
        + f"/tenant/v1/governance/schema_templates/{item_id}",
        params=params,
        headers=context.config.userdata[tenant]["auth_headers"],
    )
    return response


def update_schema_template(context, tenant, item_id, payload):
    response = requests.put(
        context.config.userdata.get("traction_host")
        + f"/tenant/v1/governance/schema_templates/{item_id}",
        json=payload,
        headers=context.config.userdata[tenant]["auth_headers"],
    )
    return response


def delete_schema_template(context, tenant, item_id):
    response = requests.delete(
        context.config.userdata.get("traction_host")
        + f"/tenant/v1/governance/schema_templates/{item_id}",
        headers=context.config.userdata[tenant]["auth_headers"],
    )
    return response


def create_credential_template(context, tenant, payload):
    response = requests.post(
        context.config.userdata.get("traction_host")
        + "/tenant/v1/governance/credential_templates/",
        json=payload,
        headers=context.config.userdata[tenant]["auth_headers"],
    )
    return response


def list_credential_templates(context, tenant, params):
    response = requests.get(
        context.config.userdata.get("traction_host")
        + "/tenant/v1/governance/credential_templates",
        params=params,
        headers=context.config.userdata[tenant]["auth_headers"],
    )
    return response


def get_credential_template(context, tenant, item_id, params: dict | None = {}):
    response = requests.get(
        context.config.userdata.get("traction_host")
        + f"/tenant/v1/governance/credential_templates/{item_id}",
        params=params,
        headers=context.config.userdata[tenant]["auth_headers"],
    )
    return response


def update_credential_template(context, tenant, item_id, payload):
    response = requests.put(
        context.config.userdata.get("traction_host")
        + f"/tenant/v1/governance/credential_templates/{item_id}",
        json=payload,
        headers=context.config.userdata[tenant]["auth_headers"],
    )
    return response


def delete_credential_template(context, tenant, item_id):
    response = requests.delete(
        context.config.userdata.get("traction_host")
        + f"/tenant/v1/governance/credential_templates/{item_id}",
        headers=context.config.userdata[tenant]["auth_headers"],
    )
    return response


def send_message(context, tenant, contact_id, content):
    data = {"contact_id": contact_id, "content": content}
    response = requests.post(
        context.config.userdata.get("traction_host")
        + "/tenant/v1/messages/send-message",
        json=data,
        headers=context.config.userdata[tenant]["auth_headers"],
    )
    return response


def list_messages(context, tenant, params):
    response = requests.get(
        context.config.userdata.get("traction_host") + "/tenant/v1/messages",
        params=params,
        headers=context.config.userdata[tenant]["auth_headers"],
    )
    return response


def get_message(context, tenant, item_id, params: dict | None = {}):
    response = requests.get(
        context.config.userdata.get("traction_host") + f"/tenant/v1/messages/{item_id}",
        params=params,
        headers=context.config.userdata[tenant]["auth_headers"],
    )
    return response


def update_message(context, tenant, item_id, payload):
    response = requests.put(
        context.config.userdata.get("traction_host") + f"/tenant/v1/messages/{item_id}",
        json=payload,
        headers=context.config.userdata[tenant]["auth_headers"],
    )
    return response


def delete_message(context, tenant, item_id):
    response = requests.delete(
        context.config.userdata.get("traction_host") + f"/tenant/v1/messages/{item_id}",
        headers=context.config.userdata[tenant]["auth_headers"],
    )
    return response
