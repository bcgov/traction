FROM python:3.13-slim AS base
WORKDIR /usr/src/app

# Install and configure poetry
USER root

ENV POETRY_VERSION=1.6.1
ENV POETRY_HOME=/opt/poetry
RUN apt-get update && apt-get install -y curl && apt-get clean
RUN curl -sSL https://install.python-poetry.org | python -

ENV PATH="/opt/poetry/bin:$PATH"
RUN poetry config virtualenvs.in-project true

# Setup project
RUN mkdir traction_innkeeper && touch traction_innkeeper/__init__.py
COPY pyproject.toml poetry.lock README.md ./
ARG install_flags=--no-dev
RUN poetry install ${install_flags}
USER $user

FROM python:3.13-bullseye
WORKDIR /usr/src/app
COPY --from=base /usr/src/app/.venv /usr/src/app/.venv
ENV PATH="/usr/src/app/.venv/bin:$PATH"

COPY traction_innkeeper/ traction_innkeeper/
COPY docker/default.yml ./

ENTRYPOINT ["/bin/bash", "-c", "aca-py \"$@\"", "--"]
CMD ["start", "--arg-file", "default.yml"]