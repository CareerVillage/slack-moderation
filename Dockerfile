FROM python:3.14.7-slim-trixie

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV C_FORCE_ROOT True

RUN apt-get clean && \
    apt-get update -y && \
    apt-get install -y \
    nginx \
    postgresql-client \
    curl \
    gcc \
    && apt-get upgrade -y \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /moderation/src
WORKDIR /moderation

COPY .env .

# Install infisical CLI
RUN curl -1sLf 'https://dl.cloudsmith.io/public/infisical/infisical-cli/setup.deb.sh' | bash
RUN curl -1sLf 'https://artifacts-cli.infisical.com/setup.deb.sh' | bash \
    && apt-get update && apt-get install -y --no-install-recommends infisical \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

RUN pip install ipython

COPY ./src /moderation/src

WORKDIR /moderation/src

ENTRYPOINT ["/moderation/src/docker-entrypoint.sh"]
