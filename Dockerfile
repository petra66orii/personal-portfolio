# Step 1: Build the frontend
FROM node:20-alpine AS frontend

WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm install
COPY frontend ./
RUN npm run build

# Debugging: Verify the dist directory exists
RUN ls -R /app/frontend/dist || echo "dist directory not found"

# Step 2: Set up the backend
FROM python:3.12-slim AS backend

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y build-essential libpq-dev && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --upgrade pip && pip install -r ./backend/requirements.txt

# Copy backend code
COPY backend ./backend
COPY portfolio ./portfolio
COPY manage.py ./
COPY db.sqlite3 ./
COPY media ./media
COPY templates ./templates

# Copy built frontend into backend's static files
COPY --from=frontend /app/frontend/dist ./staticfiles

# Copy frontend index.html to templates directory for Django to serve
COPY --from=frontend /app/frontend/dist/index.html ./templates/index.html

# Fix asset paths in the template to match Django's STATIC_URL - handle any filename
RUN sed -i 's|/assets/|/static/assets/|g' /app/templates/index.html

# Debug: Show what files we actually have
RUN echo "=== Assets in staticfiles/assets ===" && ls -la /app/staticfiles/assets/ || echo "No assets directory"
RUN echo "=== Template index.html content ===" && cat /app/templates/index.html | grep -E "(\.js|\.css)"

# Ensure staticfiles directory exists and is writable
RUN mkdir -p /app/staticfiles && chmod -R 755 /app/staticfiles
RUN mkdir -p /app/collected_static && chmod -R 755 /app/collected_static

# Ensure media directories exist
RUN mkdir -p /app/media && chmod -R 755 /app/media

# Debugging: List contents of the root directory
RUN ls -R /app

# Set environment variables for Django
ENV DJANGO_SETTINGS_MODULE=backend.settings
ENV PYTHONPATH=/app

# Collect static files
RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
