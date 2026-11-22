#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate --noinput

# Seed demo content only on the first deploy, so later admin edits are kept.
if ! python manage.py shell -c "import sys; from clinic.models import Service; sys.exit(0 if Service.objects.exists() else 1)"; then
  python manage.py seed_demo
fi

# Create the admin account once, using the env vars configured on Render.
if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
  python manage.py createsuperuser --noinput || true
fi
