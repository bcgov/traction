## prerequisites

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


##### run bdd tests

in one terminal, start traction api

```sh
docker-compose up
```

once api is fully running, open a second terminal and run the bdd tests

```sh
docker-compose -f docker-compose.bdd.yml up
```