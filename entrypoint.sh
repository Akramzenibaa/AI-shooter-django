#!/bin/sh

# Exit immediately if a command exits with a non-zero status
set -e

# Run migrations
# Run migrations
echo "Run migrations..."
python manage.py wait_for_db
python manage.py migrate
python manage.py createsuperuser --noinput || true # Create admin if env vars are provided

# Migrate local images to Cloudinary automatically on startup
if [ -n "$CLOUDINARY_CLOUD_NAME" ]; then
    echo "Cloudinary credentials found. Running image migration script..."
    python manage.py migrate_to_cloudinary || true
else
    echo "Cloudinary credentials not found. Skipping migration."
fi


# Collect static files
echo "Collect static files..."
python manage.py collectstatic --noinput

# Start server
echo "Starting Gunicorn..."
exec gunicorn --bind 0.0.0.0:8000 --timeout 300 --workers 3 config.wsgi:application
