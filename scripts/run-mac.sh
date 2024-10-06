#!/bin/bash

# MAC OS Options
if [[ $OSTYPE == 'darwin'* ]]; then
  # Set default platform to linux/amd64 when running on Arm based MAC since there are no arm based images available currently.
  architecture=$(uname -m)
  if [[ "${architecture}" == 'arm'* ]] || [[ "${architecture}" == 'aarch'* ]]; then
    export DOCKER_DEFAULT_PLATFORM=linux/amd64
  fi

  # Set the date and stat options appropriately for MAC OS.
  export TA_RATIFICATION_TIME_OPS='-jf '%Y-%m-%dT%H:%M:%S%Z' +%s '
  export STAT_OPS='-f '%A''
fi

cd ../plugins/docker
docker build -f ./Dockerfile --tag traction:plugins-acapy ..
cd ../../services/aca-py
docker build -f ./Dockerfile.acapy --tag traction:traction-agent .
cd ../../scripts
docker compose up 