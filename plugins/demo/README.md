TBD - this will have docker-compose and different configs for various scenarios (different plugins, different acapy configs etc)
it should build image(s) based on ../docker/Dockerfile

We need more and varied configurations, and we need to parameterize the compose file (port numbers, passwords etc).

Currently will run at localhost:3000 (http), localhost:3001 (admin), and localhost:3002 (websockets).
Loads up a postgres database for acapy (localhost:5432).


### build and run
```
cd demo
docker-compose build
docker-compose up
```

### down and cleanup
```
cd demo
docker-compose down
docker-compose down -v --remove-orphans
```
