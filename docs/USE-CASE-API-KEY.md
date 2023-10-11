# Traction Tenant API Keys

## Traction Access
As a consumer of Traction, REST API calls to do actions with your Wallet are secured with a bearer token. To get this bearer token you need to use a secret that is tied to your Traction Tenant. A Traction Tenant can be thought of the "account" represeting your Wallet in the Traction system

To get an access token for Traction usage you can use either
- Your Wallet Secret
- An API Key you can generate as the Tenant (owner of the Wallet)

For real world operational use, API Keys are a suggested path rather than the Wallet credentials.

## Wallet Details
The Wallet details are what the person who first creates the Traction Tenant/Wallet gets back once the Tenant is approved for creation.

![image](https://github.com/bcgov/traction/assets/17445138/786a364d-7af1-4e5a-b27b-4c896891e80b)

To fetch a Bearer Token with the Wallet details you can call the `/multitenancy/wallet/{wallet_id}/token` endpoint

![image](https://github.com/bcgov/traction/assets/17445138/38fff09e-e767-4087-8b87-516d3dc20fe0)

(the Swagger documentation here can be found at `<TRACTION URL>/api/doc#/multitenancy/post_multitenancy_wallet__wallet_id__token`)

### Guidelines about Wallet credentials
As mentioned, there are important caveats to keep in mind if using these Wallet details operationally to access Traction.
The key for the Wallet is not just a Traction access secret, but also cryptographically related to transactions made by your Wallet on the ledger. As such it is crucial to keep these credentials secure.
While they can be used to call the Traction API and to log into the Tenant UI, exposing these credentials to multiple integration points or allowing multiple users (who may not be associated with the Traction Tenant in the future) to know the credentials is not advised.

The credentials for the Wallet:
- Are not retrievable if lost
- Can not be revoked or expired
- Can not have more than one

As such, a Traction Tenant API Key is much more flexible and desirable to use in Line of Business integrations, or for users to access the Tenant UI.

## What is an API Key
A Traction Tenant API Key is just another pair of ID/Key that can be used to get a Traction token to access the Traction REST API, same as the Wallet credentials.

You can self-serve create/delete API Keys as the Wallet owner, and you can create multiple of them for different integrations or users.
An API Key can be used to log into the Tenant UI (which is also just getting a Traction token upon login).

API Keys are the reccomended manner of controlling access to your Traction Tenant.

API Keys are stored as salt/hash in the Traction DB and are not able to be decoded by anyone. If an API Key is lost, a new one would have to be created.

## Get API Key
The first API key will need to be created by the Tenant/Wallet owner (IE the authoritative person who created the Tenant and is the one allowed to get the pure Wallet credentials that first time). At this time there is not support for getting an API Key at Tenant creation time, but could be a future paradigm.

The API Key can be created through the Tenant UI. Log in as your Tenant (either with the initial Wallet credentials, or with a previously created API Key) and access your API Key list from the profile button.

![image](https://github.com/bcgov/traction/assets/17445138/705cef87-180f-4cb2-b5fa-bdc20c93f8aa)

From here you can see details about existing keys and create new ones (or delete existing)

Create a new API Key and give it a descriptive alias for your tracking.

![image](https://github.com/bcgov/traction/assets/17445138/a8e7a3e9-c27f-420d-9453-728b4b419308)

Once created, securely copy the API Key to your secure secret storage. As mentioned, keys are stored as salt/hash encrypted and can not be retrieved again after creation.
The Tenant ID is the Traction Tenant identifier, and it **can** be retrieved as needed, see below. All API Keys will use the Tenant ID as the "user".

![image](https://github.com/bcgov/traction/assets/17445138/287ba21f-1154-4288-ba67-324478959133)

You can also create an API Key programatically through the Traction API. See the `/tenant/authentications/api` POST endpoint in the Swagger docs for details.

## Use API Key
Just like using the Wallet credentials to get a token, you would call a token endpoint for the Tenant using the API Key in the body.

To fetch a Bearer Token with the Tenant API Key you can call the `/multitenancy/tenant/{tenant_id}/token` endpoint.
Supply the `api_key` in the body, the `wallet_key` is not needed if using an API Key.

![image](https://github.com/bcgov/traction/assets/17445138/09f1394a-5f9f-48b9-8b54-140dcf06b457)

(the Swagger documentation here can be found at `<TRACTION URL>/api/doc#/multitenancy/post_multitenancy_tenant__tenant_id__token`)

If you need to get the Tenant ID again it can be found on your **Profile page** in the Tenant UI.

Once you have an API Key it can also be used to log into the Tenant UI, and indeed this is a good use of Tenant API Keys. Project team members or operational staff **should** be using API Keys (which can be rotated and deleted) for accessing the Tenant UI rather than the pure Wallet credentials.

![image](https://github.com/bcgov/traction/assets/17445138/71cb4cad-aaec-4d66-9602-558608ee674b)
