#!/bin/bash
set -e
cd "$(dirname "$0")/.."/backend
python manage.py makemigrations --noinput
python manage.py migrate --noinput
pytest "$@"
