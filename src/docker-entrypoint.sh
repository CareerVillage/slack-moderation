#!/bin/sh

set -o errexit
set -o nounset

# Create a new Infisical token and export it as an environment variable
export INFISICAL_TOKEN=$(infisical login --method=universal-auth --client-id=${INFISICAL_CLIENT_ID} --client-secret=${INFISICAL_SECRET_KEY} --silent --plain)

# Write the Infisical environment variables to a file
infisical export --projectId=${INFISICAL_PROJECT_ID} --env=${INFISICAL_ENVIRONMENT_SLUG} --format=dotenv-export > ./.infisical.env

# Load the Infisical environment variables to the current shell
. ./.infisical.env

until pg_isready -h ${POSTGRES_HOST} -U ${POSTGRES_USER} -d ${POSTGRES_DB} -p ${POSTGRES_PORT} ; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 5
done

>&2 echo "Postgres is up - continuing"

exec "$@"
