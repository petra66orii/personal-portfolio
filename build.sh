#!/usr/bin/env bash

# install dependencies
pip install -r requirements.txt

# setup media files
python manage.py setup_media

# collect static files
python manage.py collectstatic --noinput

# run database migrations
python manage.py migrate

# load project data from fixture
python manage.py loaddata projects.json

# load skills data from fixture
python manage.py loaddata skills.json

# create superuser if not exists
python manage.py createsu
