#!/bin/sh

set -e

while ! nc -z $POSTGRES_HOST $POSTGRES_PORT; do sleep 1; done;

gunicorn auth.wsgi:app --bind 0.0.0.0:5000