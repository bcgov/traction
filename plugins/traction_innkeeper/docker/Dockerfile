FROM python:3.13-slim AS base
WORKDIR /usr/src/app

# Install and configure poetry
USER root

# Verify Python 3.13 is available
RUN python3 --version

ENV POETRY_VERSION=2.1.1
ENV POETRY_HOME=/opt/poetry
ENV POETRY_NO_INTERACTION=1
ENV POETRY_VENV_IN_PROJECT=1

RUN apt-get update && apt-get install -y curl && apt-get clean
RUN curl -sSL https://install.python-poetry.org | python3 -

ENV PATH="/opt/poetry/bin:$PATH"
RUN poetry config virtualenvs.in-project true

# Setup project
RUN mkdir traction_innkeeper && touch traction_innkeeper/__init__.py
COPY pyproject.toml poetry.lock README.md ./
ARG install_flags=--no-dev
# Remove any existing virtual environment and explicitly use Python 3.13
RUN rm -rf .venv || true
RUN poetry env use /usr/local/bin/python3
RUN poetry install ${install_flags}

FROM python:3.13-slim
WORKDIR /usr/src/app
COPY --from=base /usr/src/app/.venv /usr/src/app/.venv
ENV PATH="/usr/src/app/.venv/bin:$PATH"

COPY traction_innkeeper/ traction_innkeeper/
COPY docker/default.yml ./

ENTRYPOINT ["/bin/bash", "-c", "aca-py \"$@\"", "--"]
CMD ["start", "--arg-file", "default.yml"]