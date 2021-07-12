#!/bin/sh

set -o errexit
set -o nounset

python manage.py migrate
python manage.py collectstatic -c --noinput

uwsgi --module moderation.wsgi:application --master --socket :8000 --buffer-size 32768 --processes 2 --threads 2 --harakiri 40 --max-requests 5000 --vacuum --enable-threads --single-interpreter --thunder-lock
