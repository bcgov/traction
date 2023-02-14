# Tenant LOB
This is a simple server meant to represent a tenant's line of business application. 
In this demonstration, we will illustrate adding webhooks to your tenant so Aca-Py can notify you as events occur.  

It will be up to your business needs to interpret the notification topics, events and payloads to determine what your application needs to do (if anything). 

There are some simple task endpoints to help seed the system.

- create a set of 3 tenants ready to receive webhook data: alice, faber, acme
- quickly connect alice with faber and alice with acme
- view webhook event data (per tenant)
- register a public did for a tenant

Most Line of Business applications will not have multiple tenants, so our single webhook endpoint for multiple tenants is contrived. However, it does illustrate the use of API Key per tenant and how to prove the webhook data is related to your tenant (via `x-wallet-id` header).

The endpoints in this demo use `GET` for creates instead of `POST` to simplify the procedures. This will allow you to open a browser and execute the demo steps.

All data in this demo is completely ephemeral, it only exists in memory.

## Simple Demo Flow
Assumes this is being run in a local environment stood up according to [scripts](../../scripts) documentation with default configuration.

1. Create set of demo tenants
    1. Open browser at [http://localhost:9876/tasks/create-alice-faber-acme](http://localhost:9876/tasks/create-alice-faber-acme)
    2. alice, faber, and acme tenants are created
    3. each has updated their tenant config to include the webhook url with a unique api key: `http://host.docker.internal:9876/webhook#<an api key>`
    4. Note: in the docker terminal, each of the tenant's `wallet_id`, `wallet_key` and tokens are printed out. You could use these to login to [tenant-ui](http://localhost:5101)
2. Connect demo tenants 
    1. Open browser at [http://localhost:9876/tasks/connect-alice-faber-acme](http://localhost:9876/tasks/connect-alice-faber-acme)
    2. alice and faber are connected, alice and acme are connected
    3. since all tenants have registered webhooks, they will receive notifications as their tenants auto-accept connections
    4. Open browser at [http://localhost:9876/tenants/alice/webhook-data](http://localhost:9876/tenants/alice/webhook-data) to view alice's webhook data.
    5. Open browser at [http://localhost:9876/tenants/faber/webhook-data](http://localhost:9876/tenants/faber/webhook-data) to view faber's webhook data.
    6. Open browser at [http://localhost:9876/tenants/acme/webhook-data](http://localhost:9876/tenants/acme/webhook-data) to view acme's webhook data.
    7. Note that the topics are `connections` (and possibly `ping`).
    8. Note that each tenant has a unique set of data that belongs specifically to them - this is private data shared through their webhook secured with their api key.
3. Get faber a Public DID 
    1. Open browser at [http://localhost:9876/tenants/faber/public-did](http://localhost:9876/tenants/faber/public-did)
    2. This will take some time, but faber will be connected to an endorser and create a public did and write that to the ledger
    3. You will see that faber has a new attribute: `public_did`.
    4. Open browser at [http://localhost:9876/tenants/faber/webhook-data](http://localhost:9876/tenants/faber/webhook-data) to view faber's webhook data.
    5. Note that there is a new topic: `endorse_transaction`. This is faber asking the endorser to do work (write public did to ledger) on their behalf.

When creating your own tenants in the [tenant-ui](http://localhost:5101), you can update their webhook url to `http://host.docker.internal:9876/webhook` and do not add an api key. You can see notifications for you webhook in the `tenant-lob` docker console.


### Docker Build image

```shell
docker build -f Dockerfile -t tenant-lob .
```

