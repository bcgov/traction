# Showcase Application

## Architecture

The Traction Showcase App is a front end implementing (at this time) the "Alice, Faber, Acme" demo use case to show an example Line Of Business application usage of Traction.

The showcase app is a separate standalone application from Traction and consists of the following parts

- The showcase API. A REST API built on FastAPI. Interacts with Traction, and does "showcase LOB" business logic.
- The showcase front end. A VUE SPA served from the root (/) of the showcase API and calling the showcase API for all actions.
- A Postgres database keeping showcase app LOB data etc

So the showcase app needs to talk to an existing Traction and Aca-py environment to perform its functionality.

## Local Development/Usage

The Showcase Application interfaces with a Traction/Aca-py environment so standing up just the showcase app won't do much. The Traction repo docker compose scripts (in this repo at `\traction\scripts`) could be used to stand up the Traction infrastructure, and build and start up the showcase API (be sure to copy the `.env-examples` file over to a local `.env`):

`docker-compose -f docker-compose.yml -f docker-compose.showcase.yml up --build`

After this the showcase app would be accessible at `http://localhost:5200/`

### Frontend development

The Vue app is a SPA that is served by the Showcase API (see <https://github.com/bcgov/traction/blob/develop/services/showcase/api/main.py>). The build process runs Vue CLI (with `npm run build`) to build a `dist` folder that is served at the root of the API.

To develop the frontend you can make changes to the Vue app frontend code and just rebuild the Docker images as above to see the changes.

If you want to serve the Vue app in development mode (which has a lot of advantages like hot-reloading and other Vue CLI features) you can use `npm run serve` from the frontend folder then access from `http://localhost:8080/`. Though to do much in the app it will have to connect to a Traction environment. The easiest way to do this would be to just let the Traction and Showcase APIs build and deploy as described above with docker-compose, and then point the showcase frontend at the docker image showcase API.

When running in development mode (`npm run serve`) the Vue `.env.development` config file will default to point at `http://localhost:5200` (you can override this with a local if needed). This way the Vue frontend being served by Vue CLI on 8080 will talk to the showcase API and Traction being served in the docker container(s).

However, the API in the image would block calls from 8080 because of CORS, so we have an optional config in the showcase API environment that will tell the api to accept calls from 8080.
So in your `/scripts/.env` you can set the CORS allowances here:
```
# optional CORS urls for the showcase API to allow, can set for local Frontend development in your .env
SHOWCASE_CORS_URLS=http://localhost,http://localhost:8080
```

## Other

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
docker-compose exec showcase-api alembic revision --autogenerate -m "<MIGRATION COMMENT HERE>"

```

\*these are executed on startup
