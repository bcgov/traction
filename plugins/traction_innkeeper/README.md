### developer notes

- install python 3.12
- install poetry version 1.8.3

### build and run
```
cd docker
docker build -f ./Dockerfile --tag traction_innkeeper ..
docker run -it -p 3000:3000 -p 3001:3001 --rm traction_innkeeper
```

### notes for proof of concept

#### traction_innkeeper plugin

- creates an innkeeper wallet and tenant on start up (if not already created)
- we can configure the innkeeper `tenant_id` and `wallet_key`, however, we cannot configure a `wallet_id`
- prints out the traction_innkeeper wallet_id/key and a token 


*IMPORTANT* will need the `X-API-KEY` (default = change-me) for all calls in swagger

#### demo flow

1) prospective tenant (think hitting public page, possibly with captcha)

- call `/multitenancy/reservations` to start the process (provide contact info, reason etc)
- result of call is a `reservation_id`, caller will need this later for `check-in`
- todo: notification to innkeeper (and associated persons) that a request has come in

2) innkeeper

- call `/innkeeper/reservations` to list all reservations, fetch the above reservation_id
- call `/innkeeper/reservations/{reservation_id}/approve` to approve (probably a lot of out of band stuff)
- result of this call is a `reservation_pwd`, this needs to be delivered to the reservation's contact

3) prospective tenant (another public page, could be scanned from delivered qr code?)
- once prospective tenant has been approved and provided with the `reservation_pwd`, they call `/multitenancy/reservations/{reservation_id}/check-in` with the `reservation_id` and `reservation_pwd`.
- result of `/multitenancy/signin` call is `wallet_id`, `wallet_key`, `token` -> they save this themselves


#### "public" endpoints

- `POST /multitenancy/reservations`
- `POST /multitenancy/reservations/{reservation_id}/check-in`
- `POST /multitenancy/tenant/{tenant_id}/token`

We have to use /multitenancy because there are no ways to put in "public" endpoints in the admin server with multi-tenancy enabled.
These endpoints do not require a Bearer token, so we can call them from our app (app still needs X-API-KEY).  
The `/multitenancy/tenant/{tenant_id}/token` exactly mirrors the built-in `/multitenancy/wallet/{wallet_id}/token` but is called with the tenant id.  
This is useful for the innkeeper as the `tenant_id` can be configured, so it is a consistent and well known ID.  


#### innkeeper endpoints (secured to only allow innkeeper wallet/tenant - need Bearer token)

- `GET /innkeeper/reservations`
- `PUT /innkeeper/reservations/{reservation_id}/approve`
- `GET /innkeeper/tenants`
- `GET /innkeeper/tenants/{tenant_id}`

innkeeper is a "special" tenant, use middleware to restrict these calls.  
See above about innkeeper calling `/multitenancy/tenant/{tenant_id}/token` to get tokens for the innkeeper.

#### tenant endpoints (secured to any wallet/tenant - need Bearer token)
- `GET /tenant` (basically get self)

Tenants do not need to know their tenant id, we grab their wallet_id from their token and look up using that.

Still lots to flesh out, this was just proof of concept to see about data storage, flow, etc.  
