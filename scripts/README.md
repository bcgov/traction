# Overview
These scripts allow a developer (or similiarly interested party), to build and spin up a local environment of Traction (multitenant acapy + plugins + tenant ui). 

Traction is a multi-tenanted Aca-Py that is intended to aid tenants with a self-service model. To support this, there are two "roles": innkeeper and tenant. 

### Innkeeper
Innkeeper is used by the administrator of the multi-tenanted Aca-Py instance and is used to onboard tenants. There will be additional administrative functions added but currently their role is basically approval (or denial) of requests to become tenants.

### Tenants
Tenants are analogous to wallets when Aca-Py is in multitenant mode. Traction plugins add enhanced functionality to the current Aca-Py API.  Note that the "innkeeper" is also a tenant (one with some administrative abilities and responsibilites).

### Reservations
Tenants onboard to the system by making a reservation. The innkeeper will approve (or deny) the reservation. Tenants that have been given approval will then check-in and be given their keys (`wallet_id`, `wallet_key`, ability to get tokens...).

### Tenant UI
The Tenant UI is for the innkeeper AND tenants. (Prospective) Tenants can make a reservation, check the status of their reservation, check-in when approved and then login and perform necessary start up tasks for their wallet/agent (public did, connect with endorser, create schemas and credential defintions, etc).  The Innkeeper can review reservations and approve/deny, and then manage tenants.

New functionality is being added daily, so stay tuned as the Tenant UI grows. Keep in mind, the Tenant UI is *NOT* intended to support all possible functions allowed by Aca-Py, nor is it intended to act as your line of business application. The vision is to support the most necessary start up procedures and functions that are not done regularly (i.e. create a schema).

### API Proxy
For tenants to perform all their Aca-Py calls, access is done through an NGINX proxy. This allows tenants to call most all endpoints found in Aca-Py Admin plus enhancements added through the Traction Plugins. This is the API your controllers and line of business apps will call. See [NGINX Template](../plugins/docker/tenant-proxy.conf.template)


## Caveats and Cautions

### Endorser
Currently this setup has dependencies on BCovrin Test Ledger and a registered endorser DID. These constraints will be removed, they are just short term requirements that the BC Gov developers needed to communicate with phone/wallets and other DIDs on the same ledger for demonstration purposes. This is not a vision for Traction, as it should be up to the administrator/installer/devops team (and their business contraints) for endorsement. Feel free to alter the default configuration for your purposes, but understand their may be some unintended consequences and it may not work correctly.

### Plugin Image
Also, there are longer term goals for moving the plugins to separate repositories and allowing teams to pull them in and configure their own Aca-Py images as needed. Currently, we are pulling the plugins in as source and building a custom image. For local development, the build of this image is included in the `docker-compose build` command. Once the Aca-py + plugin image is built (tagged: `traction-local:acapy`), that image is pulled into another that we use to run an [ngrok]() script for external access to our agent (see [services/aca-py](../services/aca-py). This is not what we are doing in production, but we are doing it here (for now).

#### traction-local:acapy image
This image is based on [bcgovimages/aries-cloudagent:py36-1.16-1_1.0.0-rc1](https://hub.docker.com/layers/bcgovimages/aries-cloudagent/py36-1.16-1_1.0.0-rc1/images/sha256-0c2f34a84b672ee68439b5dab7db9298b7945d2f2b54c165ec346a8096b7ff31?context=explore) and this is where we pull in the [traction plugins](../plugins) and build out the image see [Dockerfile](../plugins/docker/Dockerfile)

The plugins are built using the base plugins [pyproject.toml](../plugins/pyproject.toml) which pulls in each plugin as source. Simply adding new plugin directories to the file system and adding to the dockerfile will not be enough, they must be dependencies in the `plugins/pyproject.toml`.

Stay tuned for updates to make this process simpler and more generic. It is currently in place to support some immediate needs by the BC Gov developers.


## Environment

The default configuration will stand up the following environment:

- NGROK Traction Agent. An ngrok public endpoint for acapy agent... see `ACAPY_HTTP_PORT` environment variable (8030).
- Traction Agent. Multitenanted Aca-Py with Traction Plugins
- Tenant Proxy. NGINX proxy for tenant API... see `TENANT_PROXY_PORT` environment variable  (8032).
- Traction DB. Postgresql database for Traction Agent Aca-Py
- Tenant UI. Vue 3 application for innkeeper (tenant onboarding) and tenants... see `TENANT_UI_PORT` environment variable  (5101).
- Endorser API. Controller for endorser running locally.
- Endorser Agent. Aca-Py configured for endorser role.
- Endorser DB. Postgresql database for Endorser Agent Aca-Py

### Endpoints

- [Tenant Proxy Swagger](http://localhost:8032/api/doc)
- [Tenant UI - Innkeeper](http://localhost:5101/innkeeper)
- [Tenant UI - Tenants](http://localhost:5101/)

### Credentials

- innkeeper / change-me


### External dependencies
- BCovrin Test ledger... see `ACAPY_GENESIS_URL` environment variable ([http://test.bcovrin.vonx.io/genesis](http://test.bcovrin.vonx.io/genesis)).
- previously registered Endorser DID... see `ACAPY_ENDORSER_PUBLIC_DID` environment variable.


## Run Local Traction
- docker
- docker-compose

### start

1. copy `.env-example` to `.env` and adjust as necessary for your environment
2. bring up traction

```sh
cp .env-example .env
docker-compose build
docker-compose up
```

### stop
This will leave the volume (data) intact and available on restart.

```sh
docker-compose down
```

*IMPORTANT* when envionments are torn down and then brought up, a new ngrok endpoint is created. This could cause issues reusing tenants/wallets as they will be registered with defunct ngrok endpoints.

### teardown
This will remove the volume, so next start/up will re-recreate a new environment.

```sh
docker-compose down -v --remove-orphans
```

## Simple Flow
The following guide, we will perform a simple onboarding process where you will play both the innkeeper and a tenant.  

This assumes a clean environment built and started as documented above.  
You may find it easier to just leave tabs open instead of copying and saving the IDs, passwords and keys.

1. (Tenant) Make a reservation
	1. open a new tab to act as a prospective tenant and make a reservation
	2. navigate to [http://localhost:5101](http://localhost:5101)
	3. Click on Create Request
	4. Fill in request, remember the email address and set Tenant name to something unique.
	5. Submit Request - copy the email address and Reservation ID.
2. (Innkeeper) Approve the Reservation
	1. open a new tab in a browser to perform innkeeper duties.
	2. navigate to [http://localhost:5101/innkeeper](http://localhost:5101/innkeeper)
	3. Sign-in with: 
		- Admin Name = `innkeeper`
		- Admin Key = `change-me`
	4. Go to the Reservations tab and refresh if needed.
	5. Approve the Reservation by clicking the checkmark under Actions column
	6. Copy the Reservation Password (*NOTE*: this is not happening in production, the reservation password will be delivered to the tenant by email or some other means)
3. (Tenant) Check reservation status
	1. open a new tab to act as a prospective tenant and check the reservation
	2. navigate to [http://localhost:5101](http://localhost:5101)
	3. Click on Check Status
	4. enter the email address from above and the saved Reservation ID
	5. Click Check Status and it should be approved.
	6. Enter in the Reservation password.
	7. This should be validated and you are presented with your Wallet ID and Wallet Key.
	8. Copy these down!
4. (Tenant) Sign in
	1. open new tab for the tenant
	2. navigate to [http://localhost:5101](http://localhost:5101)
	3. Enter the saved Wallet ID and Wallet Key

You can use the wallet id and key to retrieve a token and use the Tenant API.

1. Open new tab and navigate to [http://localhost:8032/api/doc](http://localhost:8032/api/doc)
2. Scroll down to [POST multitenancy/wallet/{wallet_id}/token](http://localhost:8032/api/doc#/multitenancy/post_multitenancy_wallet__wallet_id__token)
3. Expand and click Try it out.
4. Populate the body with your Wallet Key
5. Enter your Wallet ID in the `wallet_id` field.
6. Click Execute and check the response.
7. Copy the value for `token` from the response.
8. Scroll to the [top](http://localhost:8032/api/doc) (or click on a lock icon).
9. In the bottom `AuthorizationHeader (apiKey)` section, for the Value field, enter `Bearer <your token value>` and Authorize.
10. You are now logged in as your tenant/wallet/agent.
11. Scroll to [GET /tenant](http://localhost:8032/api/doc#/traction-tenant/get_tenant), expand, Try it out and Execute.
12. These are your tenant's details. Only you are authorized to fetch your tenant data.
13. 
