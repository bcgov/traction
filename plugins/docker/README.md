This will contain the dockerfile that we will build our acapy + plugins image

Lots to do here to clean up where the plugin code comes from etc...
This uses the plugins/pyproject.toml to specify a new project that includes the (local) plugins as dependencies, should probably pull in versioned ones.

The dockerfile is copying over the local plugins code, but should it? Probably should be pulling in versioned code.

### developer notes

- install python 3.6.13
- install poetry version 1.1.15
- the base docker image is python 3.6.13, so best to develop using that version

### build and run
```
cd docker
docker build -f ./Dockerfile --tag traction_plugins ..
docker run -it -p 3000:3000 -p 3001:3001 --rm traction_plugins
```
