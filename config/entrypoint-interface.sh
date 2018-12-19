#!/usr/bin/env sh
dockerize -wait tcp://database:5432
dockerize -wait tcp://redis:6379

python manage.py migrate

if [ "$DJANGO_DEBUG" = "TRUE" ]; then
    exec python3 manage.py runserver 0.0.0.0:8000
else
    python manage.py collectstatic --noinput
    exec daphne -b 0.0.0.0 -p 8000 ${PROJECT_NAME}.asgi:application
fi
