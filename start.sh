#!/usr/bin/env bash
set -o errexit

python manage.py migrate

python manage.py shell -c "
from django.contrib.auth.models import User
import os
username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'changeme123')
email    = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@maram.tn')
if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, email, password)
    print(f'Superuser {username} created.')
else:
    print(f'Superuser {username} already exists.')
"

exec gunicorn maram_project.wsgi:application --bind 0.0.0.0:$PORT --workers 2
