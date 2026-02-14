#!/bin/bash
# PersoniFi Quick Setup Script

set -e

echo "🚀 PersoniFi Setup Script"
echo "========================="

# Check prerequisites
echo "📋 Checking prerequisites..."
command -v docker >/dev/null 2>&1 || { echo "❌ Docker is required but not installed."; exit 1; }
command -v docker-compose >/dev/null 2>&1 || { echo "❌ Docker Compose is required but not installed."; exit 1; }
echo "✅ Docker and Docker Compose found"

# Create environment file if not exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your configuration"
fi

# Create environment for production if needed
if [ ! -f .env.production ]; then
    echo "📝 Creating .env.production template..."
    cp .env.production.example .env.production
fi

# Build Docker images
echo "🔨 Building Docker images..."
docker-compose build

# Start services
echo "🚀 Starting services..."
docker-compose up -d

# Wait for database
echo "⏳ Waiting for database..."
sleep 10

# Run migrations
echo "📊 Running database migrations..."
docker-compose exec -T web python manage.py migrate

# Create superuser (optional)
echo "👤 Creating superuser..."
docker-compose exec -T web python manage.py createsuperuser --noinput \
    --username admin \
    --email admin@example.com 2>/dev/null || echo "Superuser creation skipped (may already exist)"

# Collect static files
echo "📦 Collecting static files..."
docker-compose exec -T web python manage.py collectstatic --noinput

# Install testing dependencies
echo "🧪 Installing testing dependencies..."
pip install -r requirements/testing.txt 2>/dev/null || echo "Skipping (requirements already installed)"

echo ""
echo "✅ Setup complete!"
echo ""
echo "📌 Next steps:"
echo "1. Edit .env file with your configuration"
echo "2. Access the application at http://localhost:8000"
echo "3. Admin panel at http://localhost:8000/admin"
echo "4. GraphQL at http://localhost:8000/graphql"
echo "5. Run tests: pytest tests/ -v"
echo "6. Run benchmarks: pytest tests/performance/ --benchmark-only"
echo ""
echo "🛑 To stop services: docker-compose down"
echo "📝 To view logs: docker-compose logs -f"
