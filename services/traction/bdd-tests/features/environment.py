from behave import register_type

from steps.setup import _hard_delete_tenant
from pprint import pp


def parse_boolean(text):
    if text.lower() == "true":
        return True
    elif text.lower() == "false":
        return False
    raise ValueError("Expect True or False, got {}".format(text))


register_type(bool=parse_boolean)


def after_scenario(context, scenario):
    # create tenant

    tenants = [
        t
        for t in context.config.userdata.values()
        if (type(t) == dict) and "tenant_id" in t.keys()
    ]

    for tenant_config in tenants:
        if not tenant_config.get("deleted", False):
            _hard_delete_tenant(context, tenant_config)
            pass
    pass
