#!/bin/bash
set -e
cd "$(dirname "$0")/.."
python manage.py makemigrations --noinput
python manage.py migrate --noinput
pytest "$@"
