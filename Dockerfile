FROM python:3.14.7-slim-trixie

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    C_FORCE_ROOT=True \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /moderation

COPY requirements.txt ./

# build-essential/libpq-dev/curl are only needed to compile C extensions
# and install infisical. They are purged in the same layer so they do not
# stay in the final image.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        ca-certificates \
        curl \
        libpq5 \
        libpq-dev \
        libssl-dev \
        postgresql-client \
    && curl -1sLf 'https://artifacts-cli.infisical.com/setup.deb.sh' | bash \
    && apt-get update \
    && apt-get install -y --no-install-recommends infisical \
    && pip install --upgrade pip \
    && pip install -r requirements.txt \
    && pip install ipython \
    && apt-get purge -y --auto-remove build-essential libpq-dev libssl-dev curl \
    && rm -rf /var/lib/apt/lists/*

COPY ./src /moderation/src
WORKDIR /moderation/src

ENTRYPOINT ["/moderation/src/docker-entrypoint.sh"]
