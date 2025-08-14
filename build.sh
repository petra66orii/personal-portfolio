#!/usr/bin/env bash

# Install Python dependencies
pip install -r requirements.txt

# Build frontend
npm --prefix frontend install
npm --prefix frontend run build

# Copy index.html to Django templates
mkdir -p templates
cp frontend/dist/index.html templates/

# Copy assets into Django staticfiles
mkdir -p staticfiles
cp -r frontend/dist/assets staticfiles/

# Collect static
python manage.py collectstatic --noinput

# Database setup
python manage.py migrate
python manage.py loaddata projects.json
python manage.py loaddata skills.json
python manage.py createsu
