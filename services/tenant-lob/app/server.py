from aiohttp import web

from config import WEBHOOK_URL
from connect_tenants import connect_tenants
from set_public_did import set_public_did
from storage import tenants_store
from create_tenant import create_tenant


routes = web.RouteTableDef()

ALICE = "alice"
FABER = "faber"
ACME = "acme"
DEMO_NAMES = [ALICE, FABER, ACME]


def print_tenant_details(tenant):
    print(f"\ntenant.tenant_name = {tenant['tenant']['tenant_name']}")
    print(f"tenant.tenant_id = {tenant['tenant']['tenant_id']}")
    print(f"tenant.wallet_id = {tenant['tenant']['wallet_id']}")
    print(f"wallet.wallet_name = {tenant['wallet']['settings']['wallet.name']}")
    print(f"wallet.wallet_id = {tenant['wallet_id']}")
    print(f"wallet.wallet_key = {tenant['wallet_key']}")
    print(f"\nBearer {tenant['token']}")


async def get_or_create_tenant(name):
    if name not in tenants_store.keys():
        tenant = await create_tenant(name)
        tenants_store[name] = tenant

    tenant = tenants_store[name]
    return tenant


@routes.get("/")
async def base_url(request):
    return web.json_response({"webhook_url": WEBHOOK_URL})


# using a get to make this easy to execute in a browser
@routes.get("/tasks/create-alice-faber-acme")
async def do_create_alice_faber_acme(request: web.BaseRequest):
    result = {}
    for name in DEMO_NAMES:
        tenant = await get_or_create_tenant(name)
        result[name] = tenant

    for key in result.keys():
        print_tenant_details(result[key])
    return web.json_response(result)


@routes.get("/tasks/connect-alice-faber-acme")
async def do_connect_alice_faber_acme(request: web.BaseRequest):
    alice = await get_or_create_tenant(ALICE)
    faber = await get_or_create_tenant(FABER)
    acme = await get_or_create_tenant(ACME)

    a = await connect_tenants(alice, faber)
    b = await connect_tenants(alice, acme)

    connections = [a, b]
    return web.json_response(connections)


@routes.get("/tenants/{name:.*}/public-did")
async def get_or_create_public_did(request: web.BaseRequest):
    name = request.match_info["name"]
    if name not in tenants_store.keys():
        return web.json_response(
            status=404, body={"message": f"tenant name '{name}' does not exist"}
        )

    tenant = await get_or_create_tenant(name)
    if "public_did" in tenant.keys():
        did = tenant["public_did"]
    else:
        did = await set_public_did(tenant)

    print(f"`{name}` public did = {did}")

    return web.json_response(tenant)


@routes.get("/tenants/{name:.*}/webhook-data")
async def get_tenant_webhook_data(request: web.BaseRequest):
    name = request.match_info["name"]
    if name not in tenants_store.keys():
        return web.json_response(
            status=404, body={"message": f"tenant name '{name}' does not exist"}
        )

    tenant = await get_or_create_tenant(name)

    return web.json_response(tenant["webhook_data"])


@routes.get("/tenants/{name:.*}")
async def do_get_or_create_tenant(request: web.BaseRequest):
    name = request.match_info["name"]

    result = {}
    tenant = await get_or_create_tenant(name)
    result[name] = tenant
    print_tenant_details(tenant)
    return web.json_response(tenant)


@routes.get("/tenants")
async def do_get_tenants(request: web.BaseRequest):
    return web.json_response(tenants_store)


#
# This is the point of the demo.
# Expose and endpoint on your line of business application that understands
# webhook data sent by acapy.
#
# Expose /webhook and Aca-py will call it with topic/<topic name>
# and the body of the POST will contain a payload.
# Payloads generally have a property reflecting the state of the event series.
#
# webhooks will have the wallet id as a header and (if provided by you) an api key so
# you can ensure that this data is for you and was provided by Aca-Py.
#
# Here, we expose one endpoint for all tenants in this LOB demo
#
@routes.post(path="/webhook/topic/{topic:.*}")
async def receive_webhook(request: web.BaseRequest):
    topic = request.match_info["topic"].strip("/")
    wallet_id = request.headers["x-wallet-id"]
    payload = await request.json()
    # since we are reusing this endpoint for all tenants,
    # let's get the correct tenant (by their wallet_id)
    # and we can verify this is called from acapy by the api_key
    try:
        api_key = request.headers["x-api-key"]
        for key in tenants_store.keys():
            t = tenants_store[key]
            if t["wallet_id"] == wallet_id and t["api_key"] == api_key:
                # only storing for demo purposes
                # one would analyze the topic, the payload, the state of payload
                # and perform some business logic accordingly
                if topic not in t["webhook_data"].keys():
                    t["webhook_data"][topic] = []

                t["webhook_data"][topic].append(payload)

    except Exception:
        # this could be for a tenant created outside of this demo...
        print(f"Received webhook for wallet_id `{wallet_id}` and topic = `{topic}`")
        print(payload)
    return web.Response(status=200)


app = web.Application()
app.add_routes(routes)


if __name__ == "__main__":
    web.run_app(app, port=8088)
