```shell
pip install -r requirements.txt
gunicorn -k uvicorn.workers.UvicornWorker -b localhost:5000  api.main:app
```

```shell
pip install tox
tox -e lint
tox -e test
```

how to generate new alembic revision, from /scripts folder

```
docker-compose exec traction-api alembic revision --autogenerate -m "<MIGRATION COMMENT HERE>"

```

\*these are executed on startup
