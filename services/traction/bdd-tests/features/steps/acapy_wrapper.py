import requests


def list_credentials(context, tenant, params: dict | None = {}):
    response = requests.get(
        context.config.userdata.get("traction_host") + f"/tenant_acapy/credentials",
        params=params,
        headers=context.config.userdata[tenant]["auth_headers"],
    )
    return response
