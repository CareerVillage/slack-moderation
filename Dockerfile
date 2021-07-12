FROM python:2.7.18-buster

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

RUN apt-get clean && \
    apt-get update -y && \
    apt-get install -y nginx \
    postgresql-client

RUN mkdir -p /moderation/src
WORKDIR /moderation

COPY requirements/base.pip ./

RUN pip install --no-cache-dir -r base.pip

COPY ./src /moderation/src

WORKDIR /moderation/src

ENTRYPOINT ["/moderation/src/docker-entrypoint.sh"]
