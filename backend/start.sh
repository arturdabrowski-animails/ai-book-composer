#!/usr/bin/env bash
# Startup script for Render.com

set -e

echo "🚀 Starting Book Composer Backend..."

# Run database migrations
echo "📊 Running database migrations..."
cd /opt/render/project/src/backend
alembic upgrade head

echo "✅ Migrations complete!"

# Start the application
echo "🌐 Starting FastAPI server..."
uvicorn app.main:app --host 0.0.0.0 --port $PORT
