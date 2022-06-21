from pprint import PrettyPrinter, pprint
from steps.setup import _hard_delete_tenant
from pprint import pp


def after_scenario(context, scenario):
    # create tenant

    tenants = [
        t
        for t in context.config.userdata.values()
        if (type(t) == dict) and "tenant_id" in t.keys()
    ]

    for tenant_config in tenants:
        if not tenant_config.get("deleted", False):
            pp(tenant_config)
            pass
            # _hard_delete_tenant(context, tenant_config)
    pass
