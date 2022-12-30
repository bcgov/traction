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
