# Traction Services

Traction services are built using [FastAPI](https://fastapi.tiangolo.com/).

Database migrations are generated using [alembic](https://alembic.sqlalchemy.org/en/latest/).

To run locally, first install local dependencies and then run using `gunicorn`:

```shell
pip install -r requirements.txt
gunicorn -k uvicorn.workers.UvicornWorker -b localhost:5000  api.main:app
```

## QA And Testing

Before submitting a pull request, run some tests locally to ensure your updates will pass the automated QA checks.

To run linting and tests locally (these are executed automatically for each PR):

```shell
pip install tox
tox -e lint
tox -e test
```

To run integration tests locally, first start all the services using docker-compose:

```shell
docker-compose up
```

... then, in a separate shell, run the tests:

```shell
docker exec scripts_traction-api_1 pytest --asyncio-mode=strict -m integtest
```

## Behaviour Driven Tests
To run 'Behave' bdd tests. start traction, then navigate to bdd-tests folder and run behave

terminal 1 (from this folder)
```shell
cd ../../scripts
docker-compose up
```
terminal 2 (from this folder)
```shell
cd bdd-tests
behave
```

## Adding a New Database Model

Add a new python model file in the `services/traction/api/db/models` directory.  You can review the existing model files for examples.

Add a new "repository" file under `services/traction/api/db/repositories` - again, you can review the existing repositories for examples.

To generate new alembic revision (this will go in the `db/migrations` directory), first update the model file(s) and then from /scripts folder:

```shell
docker-compose exec traction-api alembic revision --autogenerate -m "<MIGRATION COMMENT HERE>"
```

Or, from the root of the `services/traction` directory:

```shell
alembic revision --autogenerate -m "comment"
```

Or, start the docker services (`docker-compose up`) and then "bash" into the "traction-api" service and run the above command.

Once your migration file is generated, review the generated code (the autogenerate does not always work perfectly) - you can review the other migrations for examples.

## Adding a new traction endpoint

Traction endpoints go in the `services/traction/api/endpoints/routes` directory - there are lots of examples.

Model files (data structures for api inputs and outputs) go in the `endpoints\models` directory.

Before writing any new code, take a look at the existing code and follow any conventions that are being used.

The `endpoints/dependencies` directory contains any useful utilities that are used by the endpoints.

Any "major" functions should go in the `services/traction/api/services` directory.

Try to keep the `endpoints/routes` fairly thin (input validations, output formatting) and put any major logic into `api/services`.

## Adding a new Workflow

The `BaseWorkflow` class is in `api/services/base.py` - extend this to create a new workflow and implement any virtual methods (these throw `NotImplementedError()` in the base workflow).  The main functions of the workflow are:

- subscribe to any relevant aca-py webhooks
- create a new workflow instance
- locate the appropriate workflow on receipt of an aca-py webhook
- perform processing based on the received webhook and workflow state
- complete the workflow (when appropriate to do so)
- emit traction webhooks (to the tenant line of business application) as appropriate

TODO update this section after architectural review of the traction workflow capabilities.

## Calling Aca-py

Call Aca-py endpoints using the openapi-generated client code in `services/traction/acapy_client`.  The security headers will be injected automatically (Aca-py Admin API Key and tenant bearer token) based on the authentication provided by the traction user.

The Aca-py API classes are in `acapy_client/api` and the model files are in `acapy_client/model`, an example follows:

```
from acapy_client.api.issue_credential_v1_0_api import IssueCredentialV10Api
from acapy_client.model.cred_attr_spec import CredAttrSpec
from acapy_client.model.credential_preview import CredentialPreview
from acapy_client.model.v10_credential_free_offer_request import (
    V10CredentialFreeOfferRequest,
)

issue_cred_v10_api = IssueCredentialV10Api(api_client=get_api_client())

...

cred_preview = CredentialPreview(attributes=cred_attrs)
cred_offer = V10CredentialFreeOfferRequest(
    connection_id=str(issue_cred.connection_id),
    cred_def_id=issue_cred.cred_def_id,
    credential_preview=cred_preview,
    comment="TBD comment goes here",
    auto_issue=True,
    auto_remove=False,
)
data = {"body": cred_offer}
cred_response = issue_cred_v10_api.issue_credential_send_offer_post(**data)

...
```
