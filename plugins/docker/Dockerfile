FROM bcgovimages/von-image:py36-1.16-1 AS base
# python 3.6.13

# Install and Configure Poetry
USER root
ENV POETRY_VERSION=1.1.11
ENV POETRY_HOME=/opt/poetry
RUN curl -sSL https://install.python-poetry.org | python -

ENV PATH="/opt/poetry/bin:$PATH"
RUN poetry config virtualenvs.in-project true

# Setup project
RUN mkdir traction_plugins && touch traction_plugins/__init__.py
COPY --chown=indy:indy pyproject.toml README.md ./

# copy over our local plugins code so we can build/install them
# these should come from github or some version, published location
COPY --chown=indy:indy basicmessage_storage ./basicmessage_storage
COPY --chown=indy:indy multitenant_provider ./multitenant_provider
COPY --chown=indy:indy traction_innkeeper ./traction_innkeeper

RUN poetry install --no-dev

# Make site packages location more accessible (for use with volumes)
RUN ln -s $(poetry env info -p)/lib/python3.6/site-packages site-packages


FROM bcgovimages/aries-cloudagent:py36-1.16-1_1.0.0-rc1
COPY --from=base --chown=indy:indy /home/indy/.venv /home/indy/.venv
ENV PATH="/home/indy/.venv/bin:$PATH"

COPY --chown=indy:indy docker/default.yml ./
COPY --chown=indy:indy basicmessage_storage/basicmessage_storage traction_plugins/basicmessage_storage
COPY --chown=indy:indy multitenant_provider/multitenant_provider traction_plugins/multitenant_provider
COPY --chown=indy:indy traction_innkeeper/traction_innkeeper traction_plugins/traction_innkeeper

ENTRYPOINT ["/bin/bash", "-c", "aca-py \"$@\"", "--"]
CMD ["start", "--arg-file", "default.yml"]