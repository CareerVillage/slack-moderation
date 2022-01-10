#!/bin/sh

set -o errexit
set -o nounset

eval $(envkey-source)

until pg_isready -h ${POSTGRES_HOST} -U ${POSTGRES_USER} -d ${POSTGRES_DB} -p 5433 ; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 5
done

>&2 echo "Postgres is up - continuing"

exec "$@"
