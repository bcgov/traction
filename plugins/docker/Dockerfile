FROM ghcr.io/hyperledger/aries-cloudagent-python:py3.9-0.12.1 as base

# Install and Configure Poetry
USER root
ENV POETRY_VERSION=1.6.1
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
COPY --chown=aries:aries traction_innkeeper ./traction_innkeeper

RUN poetry install --only main

# Make site packages location more accessible (for use with volumes)
RUN ln -s $(poetry env info -p)/lib/python3.6/site-packages site-packages


FROM ghcr.io/hyperledger/aries-cloudagent-python:py3.9-0.12.1
COPY --from=base --chown=aries:aries /home/aries/.venv /home/aries/.venv
ENV PATH="/home/aries/.venv/bin:$PATH"

COPY --chown=aries:aries docker/default.yml ./
COPY --chown=aries:aries traction_innkeeper/traction_innkeeper traction_plugins/traction_innkeeper
RUN pip install git+https://github.com/hyperledger/aries-acapy-plugins@main#subdirectory=basicmessage_storage
RUN pip install git+https://github.com/hyperledger/aries-acapy-plugins@main#subdirectory=connection_update
RUN pip install git+https://github.com/hyperledger/aries-acapy-plugins@main#subdirectory=multitenant_provider
RUN pip install git+https://github.com/hyperledger/aries-acapy-plugins@main#subdirectory=rpc

ENTRYPOINT ["/bin/bash", "-c", "aca-py \"$@\"", "--"]
CMD ["start", "--arg-file", "default.yml"]
