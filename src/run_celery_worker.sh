#!/bin/sh

set -o errexit
set -o nounset

celery -A moderation worker -l info
