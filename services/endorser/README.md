# Endorser Services

Endorser services are built using [FastAPI](https://fastapi.tiangolo.com/).

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
