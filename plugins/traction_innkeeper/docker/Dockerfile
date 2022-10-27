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
RUN mkdir traction_innkeeper && touch traction_innkeeper/__init__.py
COPY --chown=indy:indy pyproject.toml poetry.lock README.md ./
RUN poetry install --no-dev

FROM bcgovimages/von-image:py36-1.16-1
COPY --from=base --chown=indy:indy /home/indy/.venv /home/indy/.venv
ENV PATH="/home/indy/.venv/bin:$PATH"

COPY docker/default.yml ./
COPY traction_innkeeper traction_innkeeper
ENTRYPOINT ["/bin/bash", "-c", "aca-py \"$@\"", "--"]
CMD ["start", "--arg-file", "default.yml"]