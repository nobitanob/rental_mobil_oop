# ============================================
# Dockerfile untuk Aplikasi Rental Mobil Web
# Framework: Django
# Python Version: 3.11
# ============================================

# Stage 1: Base image
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=rental_mobil_web.settings

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    # MySQL client library
    default-libmysqlclient-dev \
    # Build essentials for compiling Python packages
    build-essential \
    pkg-config \
    # For healthcheck
    curl \
    # Cleanup
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# ============================================
# Stage 2: Dependencies
# ============================================
FROM base as dependencies

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir gunicorn mysqlclient

# ============================================
# Stage 3: Production
# ============================================
FROM dependencies as production

# Create non-root user for security
RUN groupadd -r appgroup && useradd -r -g appgroup appuser

# Copy application code
COPY --chown=appuser:appgroup . .

# Create necessary directories
RUN mkdir -p /app/logs /app/staticfiles /app/media \
    && chown -R appuser:appgroup /app/logs /app/staticfiles /app/media

# Collect static files
RUN python manage.py collectstatic --noinput --clear || true

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/admin/ || exit 1

# Default command - use gunicorn for production
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "--threads", "2", "rental_mobil_web.wsgi:application"]

# ============================================
# Stage 4: Development (alternative target)
# ============================================
FROM dependencies as development

# Install development dependencies
RUN pip install --no-cache-dir \
    django-debug-toolbar \
    pytest \
    pytest-django \
    coverage

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/logs /app/staticfiles /app/media

# Expose port
EXPOSE 8000

# Development command - use Django dev server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
