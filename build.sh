#!/usr/bin/env bash

# Install Python dependencies
pip install -r requirements.txt

# Build the frontend
npm --prefix frontend install
npm --prefix frontend run build

# Copy index.html to Django templates folder
mkdir -p templates
cp frontend/dist/index.html templates/

# Collect static files from Django + React
python manage.py collectstatic --noinput

# Run migrations
python manage.py migrate

# Load data
python manage.py loaddata projects.json
python manage.py loaddata skills.json

# Create superuser if not exists
python manage.py createsu
