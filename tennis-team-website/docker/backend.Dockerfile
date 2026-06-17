# Django Backend Dockerfile for Tennis Team Website
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PIP_NO_CACHE_DIR=off

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    postgresql-client \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create and set working directory
WORKDIR /app

# Install Python dependencies
COPY backend/requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy backend code
COPY backend/ /app/
COPY config/ /app/config/

# Create static directory
RUN mkdir -p /app/static

# Collect static files (will be done at runtime in production)
# RUN python manage.py collectstatic --noinput

# Set permissions
RUN chown -R www-data:www-data /app/static
RUN chmod -R 755 /app/static

# Expose port
EXPOSE 8000

# Command to run the application
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "tennis_backend.wsgi:application"]