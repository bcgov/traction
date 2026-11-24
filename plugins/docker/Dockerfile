FROM ghcr.io/openwallet-foundation/acapy-agent:py3.13-1.7.0 AS base

# Install and Configure Poetry
USER root
ENV POETRY_VERSION=2.5.2
ENV POETRY_HOME=/opt/poetry
RUN apt-get update && apt-get install -y curl && apt-get clean
RUN curl -sSL https://install.python-poetry.org | python -

ENV PATH="/opt/poetry/bin:$PATH"
RUN poetry config virtualenvs.in-project true

# Setup project
RUN mkdir traction_plugins && touch traction_plugins/__init__.py
COPY --chown=aries:aries traction_innkeeper/pyproject.toml traction_innkeeper/poetry.lock README.md ./

# Install dependencies only, so this layer stays cached until the lockfile changes
RUN --mount=type=cache,target=/root/.cache/pypoetry \
    poetry install --only main --no-root

# copy over our local plugins code so we can build/install them
# these should come from github or some version, published location
COPY --chown=aries:aries traction_innkeeper ./traction_innkeeper

# Install the root package on its own; its .pth entry puts /home/aries on the venv's
# sys.path, which is how the final image resolves traction_plugins.traction_innkeeper
RUN poetry install --only-root

# Make site packages location more accessible (for use with volumes)
RUN ln -s "$(poetry env info -p)"/lib/python3.13/site-packages site-packages


FROM ghcr.io/openwallet-foundation/acapy-agent:py3.13-1.7.0
COPY --from=base --chown=aries:aries /home/aries/.venv /home/aries/.venv
ENV PATH="/home/aries/.venv/bin:$PATH"

# Installed one at a time and in this order on purpose (later installs can change
# earlier dependencies). Kept above the plugin source so code changes don't re-run them.
# The base image sets PIP_NO_CACHE_DIR, so unset it to use the cache mount.
RUN --mount=type=cache,target=/home/aries/.cache/pip,uid=1001,gid=1001 \
    unset PIP_NO_CACHE_DIR && \
    pip install git+https://github.com/openwallet-foundation/acapy-plugins@1.7.0.1#subdirectory=basicmessage_storage && \
    pip install git+https://github.com/openwallet-foundation/acapy-plugins@1.7.0.1#subdirectory=connection_update && \
    pip install git+https://github.com/openwallet-foundation/acapy-plugins@1.7.0.1#subdirectory=multitenant_provider && \
    pip install git+https://github.com/openwallet-foundation/acapy-plugins@1.7.0.1#subdirectory=rpc && \
    pip install git+https://github.com/openwallet-foundation/acapy-plugins@1.7.0.1#subdirectory=connections && \
    pip install git+https://github.com/openwallet-foundation/acapy-plugins@1.7.0.1#subdirectory=webvh && \
    pip install --no-deps git+https://github.com/openwallet-foundation/acapy-plugins@1.7.0.1#subdirectory=present_proof && \
    pip install --no-deps git+https://github.com/openwallet-foundation/acapy-plugins@1.7.0.1#subdirectory=issue_credential

COPY --chown=aries:aries docker/default.yml ./
COPY --chown=aries:aries traction_innkeeper/traction_innkeeper traction_plugins/traction_innkeeper


ENTRYPOINT ["/bin/bash", "-c", "aca-py \"$@\"", "--"]
CMD ["start", "--arg-file", "default.yml"]
