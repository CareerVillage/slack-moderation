#!/bin/sh

set -o errexit
set -o nounset

python manage.py migrate
python manage.py collectstatic -c --noinput

if [ "$ENVIRONMENT" = "Production" ]; then
    NEW_RELIC_CONFIG_FILE=newrelic.ini newrelic-admin run-program uwsgi --module moderation.wsgi:application --master --socket run/moderation.sock --chmod-socket=666 --buffer-size 32768 --processes 2 --threads 1 --max-requests 1000 --vacuum --enable-threads --single-interpreter
else
    python manage.py runserver 0.0.0.0:8000
fi
