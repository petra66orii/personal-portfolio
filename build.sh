#!/usr/bin/env bash

# install dependencies
pip install -r requirements.txt

# collect static files
python manage.py collectstatic --noinput

# run database migrations
python manage.py migrate

# load project data from fixture
python manage.py loaddata projects.json

# load project data from fixture
python manage.py loaddata skills.json

# create superuser if not exists
python manage.py createsu
