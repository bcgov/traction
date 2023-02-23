### developer notes

- install python 3.6.13
- install poetry version 1.1.15
- the base docker image is python 3.6.13, so best to develop using that version

### build and run

```
cd docker
docker build -f ./Dockerfile --tag connection_update ..
docker run -it -p 3000:3000 -p 3001:3001 --rm connection_update
```

### notes

- v1_0: the only field that is updateable is `alias`.
