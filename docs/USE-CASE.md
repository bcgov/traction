# Traction Demo

The Traction demo utilizes the Innkeeper API (tenant manager), the Tenant API and Tenant UI. The Tenant UI is a Vue 3 application that calls the Tenant API - anything that the Tenant UI does can be called through the Traction (Tenant) API directly. The Tenant UI is a convenience utility and is not required for application integration.

Tenant UI is currently under development and does not implement all the features of the Tenant API. We will be hopping around between Swagger and the Tenant UI to show:

1. Innkeeper create Tenants (including Issuer)
2. Tenant enabled for Issuance by Innkeeper completing the Issuer process
3. Issuer creating schemas and credential definitions on the ledger
4. Connecting agents
5. Issuer offering credentials
6. Holder accepting a credential offer
7. Verifier making a presentation request (asking for proof of credential)
8. Holder responding to the presentation request

There are more steps to add to the demo (ex. revoking a credential), please be patient; we will update as soon as possible.

#### Scenario
We will follow the Alice / Faber / Acme scenario.

* Alice is a student of Faber College and is applying for a job at Acme.
* Acme requires proof that Alice has a degree and is a legal adult.
* Faber can provide Alice verifiable proof of her degree and age.


### Setup

To run a local instance of traction, open a bash shell and run the following (git, docker and docker-compose are required):

```bash
git clone https://github.com/bcgov/traction.git
cd traction/scripts
cp .env-example .env
docker-compose build
docker-compose up
```

By default, this will start an environment with: 

* a postgres database for traction and aca-py data
* an endorser (database, aca-py agent and API)
* [aca-py](https://github.com/hyperledger/aries-cloudagent-python) agent in multitenancy mode (access through ngrok)
* traction API
* tenant UI

| Service | URL | Credentials |
| --- | --- | --- |
| Innkeeper API (Swagger) | http://localhost:5100/innkeeper/docs | innkeeper / change-me |
| Tenant API (Swagger) | http://localhost:5100/tenant/docs | wallet\_id / wallet\_key |
| Tenant UI | http://localhost:5101 | wallet\_id / wallet\_key |

Tenants are provided with a `wallet_id` and `wallet_key` by the Innkeeper. Only the tenant retains the `wallet_key`. 

**Important**: the tenant can currently log in to one service/interface at a time. Getting a token invalidates the previous token. This is a limitation in [aca-py](https://github.com/hyperledger/aries-cloudagent-python). 


#### Ledger

By default, these agents will be using the [BCovrin Test Ledger](http://test.bcovrin.vonx.io).



## Run the demo

### Innkeeper Create Tenants
In this stage, we act as the Innkeeper and create 3 tenants: Alice, Acme, and Faber. Faber will be enabled by the Innkeeper to act as an Issuer. 

| Tenant | Role |
| --- | --- |
| Alice | Holder |
| Acme | Verifier |
| Faber | Issuer |

As the tenants are created, make note of the response, it will contain the `wallet_id` and `wallet_key` for the tenant to login to Tenant API and UI.

* login to [Innkeeper API Swagger](http://localhost:5100/innkeeper/docs) using `innkeeper` / `change-me` as credentials
* use the `v1/tenants/check-in` API to create Alice, Acme, Faber (ensure `allow_issue_credentials` is true for Faber).
* copy response for each tenant so you can act in their role.

[Watch it here!](./assets/01-innkeeper-create-tenants.mp4)

### Faber (Issuer) create schemas and credential definitions
Faber will have to complete the approval for becoming an Issuer. This creates a connection with the Endorser and a Public DID. Faber will now make calls through the Endorser to make writes to the ledger (create schemas and credential definitions).

Once Faber is an Issuer, they will create a schema and credential definition. The credential definition is used when making credential offers to other agents.

Note that Faber has made this a revocable credential. In the future (TBD), we will demonstrate how to revoke a credential.

[aca-py](https://github.com/hyperledger/aries-cloudagent-python) will create two revocation registries when the credential definition is created (one active and one spare) - once the revocation registry is "full" (each time a credential is issued it takes one spot in the registry), aca-py will automatically make the spare registry active, and will then create a new spare (so there will always be a spare registry available).

The size of the registry is a trade-off - the larger the registry the less often a new registry will need to be created, however revocation registries tend to be very large and take a long time to create, so there is a practical maximum size.  Also, some mobile agents will download the registry, and can only deal with files up to a certain size.

A revocation registry has a maximum size. The size should be at least 4, and max 32768. Creating a revocation registry with the maximum size results in a tails file of over 8MB.  There are some metrics [here](https://github.com/bcgov/indy-tails-server#metrics-about-tails-files)


[Watch it here!](./assets/02-faber-create-schema.mp4)

### Connect agents
Agents must be connected to allow interactions such as: offer a credential, request proof. Here we will connect Alice to Faber and Alice to Acme. Note that Acme and Faber have NO connection.

[Watch it here!](./assets/03-connect-agents.mp4)

### Faber offer Alice credential
Alice needs their degree from Faber. Faber can offer them a verifiable credential representing that degree. Alice can keep that in their wallet and present that when asked for verification of a degree.

[Watch it here!](./assets/04-faber-offer-credential.mp4)

### Alice accept credential offer
Faber can offer a credential to Alice. Alice can review the contents and must choose to accept it. Only after accepting the credential offer will that credential appear in their wallet.

[Watch it here!](./assets/05-alice-accept-credential.mp4)

### Acme request proof of degree
Part of the application process at Acme includes proof of a degree. In this scenario, Acme will also ask if Alice is an adult. Note that Acme does not ask for Alice's age, only that they are 18 or older. 

Note here that Acme "knows" the credential definition id for Faber's Education Degree credentials; this could be provided through a governance document, taken from the ledger or some other out of band method.

[Watch it here!](./assets/06-acme-presentation-request.mp4)

### Alice presents proof of degree
Alice will receive notification that Acme wants a presentation of proof. Alice can review what is being asked and choose whether to respond. Alice can query for credentials that would fulfil the request and build a response. 

When Alice responds with a valid proof, Acme will be notified that their request has been fulfilled and the response is verified: Alice has a degree from Faber and is 18 or older.

[Watch it here!](./assets/07-alice-send-presentation.mp4)

### More to come
Come back as we add more functionality to Tenant UI and add more steps to this demo.

