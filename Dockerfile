FROM python:3.12-slim-bookworm

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV C_FORCE_ROOT True

RUN apt-get clean && \
    apt-get update -y && \
    apt-get install -y \
    nginx \
    postgresql-client \
    curl \
    gcc

RUN mkdir -p /moderation/src
WORKDIR /moderation

COPY .env .

# Install infisical CLI
RUN curl -1sLf 'https://dl.cloudsmith.io/public/infisical/infisical-cli/setup.deb.sh' | bash
RUN apt-get update && apt-get install -y infisical

RUN pip install --upgrade pip

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

RUN pip install ipython

COPY ./src /moderation/src

WORKDIR /moderation/src

ENTRYPOINT ["/moderation/src/docker-entrypoint.sh"]
