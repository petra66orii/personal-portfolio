#!/usr/bin/env bash

# Install Python dependencies
pip install -r requirements.txt

# Build the frontend
npm --prefix frontend install
npm --prefix frontend run build

# Ensure dist/assets exists and copy media files into it so collectstatic picks them up on Render
mkdir -p frontend/dist/assets
# Cross-platform copy of media into the frontend dist assets so collectstatic picks them up.
# Use a small Python script which works on both POSIX and Windows build agents.
python - <<'PY'
import shutil, os
src = 'media'
dst = 'frontend/dist/assets'
os.makedirs(dst, exist_ok=True)
if os.path.exists(src):
	for name in os.listdir(src):
		s = os.path.join(src, name)
		d = os.path.join(dst, name)
		try:
			if os.path.isdir(s):
				shutil.copytree(s, d, dirs_exist_ok=True)
			else:
				shutil.copy2(s, d)
		except Exception:
			# don't fail the build if copying a single file fails
			pass
PY

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

