#!/bin/bash
set -ex

# Convenience workspace directory for later use
WORKSPACE_DIR=$(pwd)

# install all ACA-Py requirements
python -m pip install --upgrade pip
#pip3 install -r requirements.txt -r requirements.askar.txt -r requirements.bbs.txt -r requirements.dev.txt -r requirements.indy.txt 

# Change some Poetry settings to better deal with working in a container
poetry config cache-dir ${WORKSPACE_DIR}/.cache
poetry config virtualenvs.in-project true
# Now install all dependencies
poetry install

export PATH=${PATH}:${WORKSPACE_DIR}/.venv/bin

# add all the requirements to the default python
poetry export --without-hashes --format=requirements.txt > requirements.txt
pip install -r requirements.txt

# install black for formatting
pip3 install black

# cleanup
rm poetry.lock
rm requirements.txt
