## prerequisites

- docker
- docker-compose

### start

1. copy `.env.example` to `.env` and adjust as necessary for your environment
2. bring up traction

```sh
cp .env-example .env.local
docker-compose build
docker-compose up
```

### stop
This will leave the volume (data) intact and available on restart.

```sh
docker-compose down
```

### teardown
This will remove the volume, so next start/up will re-recreate a new environment.

```sh
docker-compose down -v --remove-orphans
```

#### start environment only, no traction api
You may want to start all the necessary infrastructure but run the traction api in your ide or outside of docker.

`traction-agent` depends on all the other services except for `traction-api`.


```sh
docker-compose up traction-agent
```

##### teardown

```sh
docker-compose down traction-agent -v --remove-orphans
```

#### start with showcase app
This will start up traction (database, agent, endorser and api) and a showcase app (with its own database).

```sh
docker-compose -f docker-compose.yml -f docker-compose.showcase.yml up
```

##### teardown

```sh
docker-compose -f docker-compose.showcase.yml -f docker-compose.yml down -v --remove-orphans
```

##### run backend tests
```sh
docker-compose up
docker exec scripts_traction-api_1 pytest --asyncio-mode=strict
```
unit tests can be run without docker like this from `/services/traction`.(tox.ini uses pytest `--asyncio-mode=strict -m "not integtest"`)
```
tox -e test 
```
run only integration tests like this
```
docker exec scripts_traction-api_1 pytest --asyncio-mode=strict -m integtest
```