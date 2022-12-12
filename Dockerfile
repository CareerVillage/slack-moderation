FROM python:3.11-buster

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

RUN apt-get clean && \
    apt-get update -y && \
    apt-get install -y nginx \
    postgresql-client

RUN mkdir -p /moderation/src
WORKDIR /moderation

RUN pip install --upgrade pip

COPY requirements/base.pip ./

RUN pip install --no-cache-dir -r base.pip

RUN pip install ipython

COPY ./src /moderation/src

WORKDIR /moderation/src

ENTRYPOINT ["/moderation/src/docker-entrypoint.sh"]
