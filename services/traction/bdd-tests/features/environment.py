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
    pp(tenants)

    for tenant_config in tenants:
        pp(tenant_config)
        if not tenant_config.get("hard_deleted", False):
            _hard_delete_tenant(context, tenant_config)
    pass
