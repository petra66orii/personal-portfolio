#!/usr/bin/env bash

set -e  # fail on error

echo "📦 Installing Python dependencies"
pip install -r requirements.txt

echo "📦 Installing Node dependencies"
npm --prefix frontend install

echo "🛠️ Building MAIN frontend"
npm --prefix frontend run build

echo "🛠️ Building ADMIN dashboard bundle"
npm --prefix frontend run build:admin

# --- COPY MEDIA INTO dist/assets (Render quirk workaround) ---
echo "📁 Preparing dist/assets for media copy"
mkdir -p frontend/dist/assets

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
            pass
PY

# --- COPY index.html to Django templates ---
echo "📁 Copying main index.html into Django template folder"
mkdir -p templates
cp frontend/dist/index.html templates/

# --- FIX PATHS inside index.html ---
echo "🔧 Fixing static asset paths in index.html"
sed -i 's|/assets/|/static/assets/|g' templates/index.html

# --- COPY MAIN frontend build into staticfiles ---
echo "📁 Copying main dist/ into staticfiles/"
mkdir -p staticfiles
cp -r frontend/dist/* staticfiles/

# --- COPY ADMIN dashboard build into staticfiles ---
echo "📁 Copying dist-admin/ into staticfiles/"
mkdir -p staticfiles/dist-admin
cp -r frontend/dist-admin/* staticfiles/dist-admin/

# --- COLLECTSTATIC (Django + WhiteNoise) ---
echo "📦 Collecting static files"
python manage.py collectstatic --noinput

# --- MIGRATIONS ---
echo "🗃️ Running migrations"
python manage.py migrate

# --- FIXTURES (optional) ---
if [ "$LOAD_FIXTURES" = "true" ]; then
    python manage.py loaddata projects.json
    echo "Fixtures loaded"
else
    echo "Skipping fixtures (set LOAD_FIXTURES=true to load)"
fi

echo "✅ Build complete!"
