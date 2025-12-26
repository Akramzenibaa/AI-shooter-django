#!/bin/sh

# Exit immediately if a command exits with a non-zero status
set -e

# Run migrations
# Run migrations
echo "Run migrations..."
python manage.py wait_for_db
python manage.py migrate
python manage.py createsuperuser --noinput || true # Create admin if env vars are provided


# Collect static files
echo "Collect static files..."
python manage.py collectstatic --noinput

# Start server
echo "Starting Gunicorn..."
exec gunicorn --bind 0.0.0.0:8000 --timeout 300 --workers 3 config.wsgi:application
