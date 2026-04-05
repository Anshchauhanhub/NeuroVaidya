#!/bin/bash
set -e

echo "Starting NeuroVaidya Services..."

# 1. Start the Flask Scraper in the background
echo "Starting Flask scraper on port 5000..."
cd medicine_scraper
# Run gunicorn in background but NOT as a daemon so logs are visible
gunicorn app:app --bind 127.0.0.1:5000 --access-logfile - --error-logfile - &
SCRAPER_PID=$!
cd ..

# 2. Run Django Setup
echo "Running database migrations..."
python manage.py migrate

echo "Collecting static files..."
python manage.py collectstatic --noinput

# 3. Start Django via Daphne (Main process)
echo "Starting Daphne server on port 8000..."
exec daphne config.asgi:application --bind 0.0.0.0 --port 8000
