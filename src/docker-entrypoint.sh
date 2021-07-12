#!/bin/sh

set -o errexit
set -o nounset

until pg_isready -h postgres -U moderation -d moderation -p 5433 ; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 5
done

>&2 echo "Postgres is up - continuing"

exec "$@"