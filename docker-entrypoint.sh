#!/bin/bash
set -e

echo "🚀 Starting Django POS System..."

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL..."
while ! pg_isready -h $DB_HOST -p $DB_PORT -U $DB_USER 2>/dev/null; do
  echo "   PostgreSQL is unavailable - sleeping"
  sleep 1
done
echo "✅ PostgreSQL is ready!"

# Apply database migrations
echo "🔄 Applying database migrations..."
python manage.py migrate --noinput

# Create superuser if it doesn't exist
echo "👤 Creating superuser if needed..."
python manage.py shell << END
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('✅ Superuser created: admin/admin123')
else:
    print('ℹ️  Superuser already exists')
END

# Collect static files
echo "📦 Collecting static files..."
if [ -d "/app/react_frontend/dist" ]; then
    python manage.py collectstatic --noinput --clear
    echo "✅ Static files collected (including React build)"
else
    echo "⚠️  React build not found at /app/react_frontend/dist"
    echo "   Run 'npm run build' in react_frontend folder first"
    # Still try to collect Django admin static files
    python manage.py collectstatic --noinput --clear || true
fi

# Create media directories
echo "📁 Creating media directories..."
mkdir -p /app/media/category_images
mkdir -p /app/media/subcategory_images
mkdir -p /app/media/product_images
mkdir -p /app/media/avatars

echo ""
echo "✅ Setup complete!"
echo "🌐 Starting Django development server..."
echo "📍 Access the application at: http://localhost:8000"
echo "🔐 Admin panel: http://localhost:8000/admin"
echo "   Username: admin"
echo "   Password: admin123"
echo ""

# Execute the main command
exec "$@"