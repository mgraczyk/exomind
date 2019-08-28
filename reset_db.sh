#!/usr/bin/env bash
set -e
[ "$ENVIRONMENT" = "development" ] || { echo 'only for development! exiting.' ; exit 1; }
pkill psql || test $? -eq 1
psql -d postgres \
    -f <(printf 'drop database if exists exomind_dev;\ncreate database exomind_dev;\n')
#rabbitmqctl purge_queue celery

rm -f ./app/migrations/0*.py
python manage.py makemigrations
python manage.py migrate
