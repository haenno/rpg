#!/bin/bash

echo 'rpg startup...'
python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py migrate --run-syncdb    # Apply database migrations
python3 manage.py collectstatic --noinput # Collect static files
python3 manage.py loaddata db-seed.json
python3 manage.py createsuperuser \
    --noinput \
    --username $DJANGO_SUPERUSER_USERNAME \
    --email $DJANGO_SUPERUSER_EMAIL
echo 'Starting rpg in production mode (Daphne):'
exec daphne -b 0.0.0.0 -p 8642 rpg.asgi:application
