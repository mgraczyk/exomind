#!/usr/bin/env bash
set -e
[ "$ENVIRONMENT" = "development" ] || { echo 'only for development! exiting.' ; exit 1; }
pkill psql || test $? -eq 1
psql -d postgres \
    -f <(printf 'drop database if exists exomind_dev;\ncreate database exomind_dev;\n')
psql -d exomind_dev -f <(printf 'create extension citext;\n')
#rabbitmqctl purge_queue celery

python manage.py makemigrations
python manage.py migrate
