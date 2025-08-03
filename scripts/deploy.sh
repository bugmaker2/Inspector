#!/bin/bash

# Inspector Deployment Script

set -e

echo "🚀 Inspector Deployment Script"
echo "======================================"

# Check if .env file exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp env.example .env
    echo "⚠️  Please edit .env file with your configuration before continuing"
    echo "   Required: OPENAI_API_KEY"
    echo "   Optional: GITHUB_TOKEN, LINKEDIN_USERNAME, LINKEDIN_PASSWORD"
    exit 1
fi

# Check if required environment variables are set
if ! grep -q "OPENAI_API_KEY=your-openai-api-key-here" .env; then
    echo "✅ Environment configuration looks good"
else
    echo "⚠️  Please configure your OpenAI API key in .env file"
    exit 1
fi

# Install dependencies
echo "📦 Installing dependencies..."
uv sync

# Create logs directory
echo "📁 Creating logs directory..."
mkdir -p logs

# Run database migrations (if using Alembic)
if [ -f "alembic.ini" ]; then
    echo "🗄️  Running database migrations..."
    uv run alembic upgrade head
fi

# Start the application
echo "🚀 Starting Inspector..."
echo "   API will be available at http://localhost:8000"
echo "   API documentation at http://localhost:8000/docs"
echo "   Press Ctrl+C to stop"

uv run python main.py 