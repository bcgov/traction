# traction [![Lifecycle:Maturing](https://img.shields.io/badge/Lifecycle-Maturing-007EC6)](<Redirect-URL>)
[![Maintainability](https://api.codeclimate.com/v1/badges/e6df50041dd4373c7e15/maintainability)](https://codeclimate.com/github/bcgov/traction/maintainability)
[![Behaviour Driven Tests](https://github.com/bcgov/traction/actions/workflows/run_bdd_tests_dev.yml/badge.svg)](https://github.com/bcgov/traction/actions/workflows/run_bdd_tests_dev.yml)

Hyperledger Aries Traction - a digital wallet solution for organizations. The focus of Traction is for line of businesses to easily integrate Aries (aca-py) into their applications; without having to stand up, maintain and manage and instance of aca-py themselves.

Traction provides a service layer to manage Aries agent instances in a multi-tenant aca-py deployment, and provides some value-add services for using aca-py functions such as setting up issuer agents, and issuing and verifying credentials.  Future functionality could include machine-readable governance, etc.

## Quick start

To run a local instance of traction, open a bash shell and run the following (git, docker and docker-compose are required):

```bash
git clone https://github.com/bcgov.traction.git
cd traction/scripts
cp .env-example .env
docker-compose build
docker-compose up
```

Open the following in a browser: `http://localhost:5100/innkeeper/docs` - this is the swagger UI for the innkeeper.

After you authenticate using `innkeeper/change-me` you can create a new tenant using the `/tenant/check-in` function.  Make a note of the `wallet_id` and `wallet_key` - you will need these to access traction as a tenant.

Open another browser and connect to `http://localhost:5100/tenant/docs`.  Authenticate using the `wallet_id/wallet_key` from the previous step.

See the [use case](./docs/USE-CASE.md) document for more detailed information about traction services.

To run the showcase application, open a second bash shell and run the following:

```bash
cd traction/scripts
docker-compose -f docker-compose.showcase.yml build
docker-compose -f docker-compose.showcase.yml up
```

Open a browser to `http://localhost:5200` to access the showcase application.

See the [use case](./docs/USE-CASE.md) document for more detailed information about how to run the showcase demo.

## Running traction

For more information about the Docker Compose files for spinning up local instances of Traction and the Showcase application:

[Scripts](./scripts/README.md)

## Deploying Traction

Helm charts for deploying Traction, Showcase and Endorser to Openshift:

[Charts](./charts/README.md)

## Developing traction

Overview of the traction architecture:

[Architecture](./docs/ARCHITECTURE.md)

Source code for Traction API:

[Traction](./services/traction/README.md)

Source code for the traction showcase demo:

[Traction Showcase/Demo](./services/showcase/README.md)

Source code for Endorser controller application.

[Endorser](./services/endorser/README.md)
