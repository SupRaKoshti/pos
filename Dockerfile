# Stage 1: Build React Frontend
FROM node:18-alpine AS frontend-builder

WORKDIR /frontend

# Copy React app
COPY react_frontend/package*.json ./
RUN npm install

COPY react_frontend/ ./
RUN npm run build

# Stage 2: Django Backend
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    libpq-dev \
    gcc \
    gettext \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy Django project
COPY . /app/

# Copy React build from stage 1
COPY --from=frontend-builder /frontend/dist /app/react_frontend/dist

# Create directories
RUN mkdir -p /app/staticfiles /app/media

# Make entrypoint executable
COPY docker-entrypoint.sh /app/
RUN chmod +x /app/docker-entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/app/docker-entrypoint.sh"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]