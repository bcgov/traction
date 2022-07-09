import requests


def convert_value(value: str):
    if value == "None":
        return None
    if value == "True":
        return True
    if value == "False":
        return False
    return value


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


def get_tenant_self(context, tenant):
    response = requests.get(
        context.config.userdata.get("traction_host") + "/tenant/v1/admin/self",
        headers=context.config.userdata[tenant]["auth_headers"],
    )
    return response


def tenant_make_issuer(context, tenant: str):
    response = requests.post(
        context.config.userdata.get("traction_host") + "/tenant/v1/admin/make-issuer",
        headers=context.config.userdata[tenant]["auth_headers"],
    )
    return response


def tenant_get_configuration(context, tenant):
    response = requests.get(
        context.config.userdata.get("traction_host")
        + f"/tenant/v1/admin/configuration",
        headers=context.config.userdata[tenant]["auth_headers"],
    )
    return response


def tenant_update_configuration(context, tenant, payload: dict):
    response = requests.put(
        context.config.userdata.get("traction_host")
        + f"/tenant/v1/admin/configuration",
        json=payload,
        headers=context.config.userdata[tenant]["auth_headers"],
    )
    return response


def innkeeper_get_permissions(context, tenant):
    tenant_id = context.config.userdata[tenant]["tenant_id"]
    response = requests.get(
        context.config.userdata.get("traction_host")
        + f"/innkeeper/v1/tenants/{tenant_id}/permissions",
        headers=context.config.userdata["innkeeper_auth_headers"],
    )
    return response


def innkeeper_update_permissions(context, tenant, payload: dict):
    tenant_id = context.config.userdata[tenant]["tenant_id"]
    payload["tenant_id"] = tenant_id
    response = requests.put(
        context.config.userdata.get("traction_host")
        + f"/innkeeper/v1/tenants/{tenant_id}/permissions",
        json=payload,
        headers=context.config.userdata["innkeeper_auth_headers"],
    )
    return response


def list_holder_credentials(context, tenant, params: dict | None = {}):
    response = requests.get(
        context.config.userdata.get("traction_host") + "/tenant/v1/holder/credentials",
        params=params,
        headers=context.config.userdata[tenant]["auth_headers"],
    )
    return response


def accept_holder_credential(context, tenant, holder_credential_id):
    data = {"holder_credential_id": holder_credential_id}
    response = requests.post(
        context.config.userdata.get("traction_host")
        + f"/tenant/v1/holder/credentials/{holder_credential_id}/accept-offer",
        json=data,
        headers=context.config.userdata[tenant]["auth_headers"],
    )
    return response


def get_holder_credential(context, tenant, item_id, params: dict | None = {}):
    response = requests.get(
        context.config.userdata.get("traction_host")
        + f"/tenant/v1/holder/credentials/{item_id}",
        params=params,
        headers=context.config.userdata[tenant]["auth_headers"],
    )
    return response
