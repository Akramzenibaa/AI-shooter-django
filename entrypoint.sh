#!/bin/sh

# Exit immediately if a command exits with a non-zero status
set -e

# Run migrations
echo "Run migrations..."
python manage.py migrate

# Collect static files
echo "Collect static files..."
python manage.py collectstatic --noinput

# Start server
echo "Starting Gunicorn..."
exec gunicorn --bind 0.0.0.0:8000 config.wsgi:application
