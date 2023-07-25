FROM ghcr.io/hyperledger/aries-cloudagent-python:py3.9-0.9.0-rc0 as base

# Install and Configure Poetry
USER root
ENV POETRY_VERSION=1.4.2
ENV POETRY_HOME=/opt/poetry
RUN apt-get update && apt-get install -y curl && apt-get clean
RUN curl -sSL https://install.python-poetry.org | python -

ENV PATH="/opt/poetry/bin:$PATH"
RUN poetry config virtualenvs.in-project true

# Setup project
RUN mkdir traction_plugins && touch traction_plugins/__init__.py
COPY --chown=aries:aries pyproject.toml README.md ./

# copy over our local plugins code so we can build/install them
# these should come from github or some version, published location
COPY --chown=aries:aries basicmessage_storage ./basicmessage_storage
COPY --chown=aries:aries connection_update ./connection_update
COPY --chown=aries:aries multitenant_provider ./multitenant_provider
COPY --chown=aries:aries traction_innkeeper ./traction_innkeeper

RUN poetry install --no-dev

# Make site packages location more accessible (for use with volumes)
RUN ln -s $(poetry env info -p)/lib/python3.6/site-packages site-packages


FROM ghcr.io/hyperledger/aries-cloudagent-python:py3.9-0.9.0-rc0
COPY --from=base --chown=aries:aries /home/aries/.venv /home/aries/.venv
ENV PATH="/home/aries/.venv/bin:$PATH"

COPY --chown=aries:aries docker/default.yml ./
COPY --chown=aries:aries basicmessage_storage/basicmessage_storage traction_plugins/basicmessage_storage
COPY --chown=aries:aries connection_update/connection_update traction_plugins/connection_update
COPY --chown=aries:aries multitenant_provider/multitenant_provider traction_plugins/multitenant_provider
COPY --chown=aries:aries traction_innkeeper/traction_innkeeper traction_plugins/traction_innkeeper

ENTRYPOINT ["/bin/bash", "-c", "aca-py \"$@\"", "--"]
CMD ["start", "--arg-file", "default.yml"]