# Traction Services

Traction services are built using [FastAPI](https://fastapi.tiangolo.com/).

Database migrations are generated using [alembic](https://alembic.sqlalchemy.org/en/latest/).

To install local dependencies:

```shell
pip install -r requirements.txt
gunicorn -k uvicorn.workers.UvicornWorker -b localhost:5000  api.main:app
```

To run linting and tests locally (these are executed automatically for each PR):

```shell
pip install tox
tox -e lint
tox -e test
```

To generate new alembic revision, first update the model file(s) and then from /scripts folder:

```shell
docker-compose exec traction-api alembic revision --autogenerate -m "<MIGRATION COMMENT HERE>"
```

Or, from the root of the `services/traction` directory:

```shell
alembic revision --autogenerate -m "comment"
```

Or, start the docker services (`docker-compose up`) and then "bash" into the "traction-api" service and run the above command.

\*these are executed on startup
