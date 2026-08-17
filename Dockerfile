FROM python:3.14.7-slim-trixie

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    C_FORCE_ROOT=True \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /moderation

COPY requirements.txt ./

# gcc/libpq-dev/curl are only needed to build wheels and install infisical.
# They are purged in the same layer so they do not stay in the final image.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        gcc \
        libpq5 \
        libpq-dev \
        postgresql-client \
    && curl -1sLf 'https://artifacts-cli.infisical.com/setup.deb.sh' | bash \
    && apt-get update \
    && apt-get install -y --no-install-recommends infisical \
    && pip install --upgrade pip \
    && pip install -r requirements.txt \
    && pip install ipython \
    && apt-get purge -y --auto-remove gcc libpq-dev curl \
    && rm -rf /var/lib/apt/lists/*

COPY ./src /moderation/src
WORKDIR /moderation/src

ENTRYPOINT ["/moderation/src/docker-entrypoint.sh"]
