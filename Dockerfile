FROM python:3.12-slim-bookworm

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

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
COPY .envkey .

# install envkey-source
RUN VERSION=$(curl https://envkey-releases.s3.amazonaws.com/latest/envkeysource-version.txt) \
  && curl -s https://envkey-releases.s3.amazonaws.com/envkeysource/release_artifacts/$VERSION/install.sh | bash
RUN eval $(envkey-source)

RUN pip install --upgrade pip

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

RUN pip install ipython

COPY ./src /moderation/src

WORKDIR /moderation/src

ENTRYPOINT ["/moderation/src/docker-entrypoint.sh"]
