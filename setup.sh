#!/bin/bash

# FastAPI Agentic RAG Setup Script

echo "🚀 FastAPI Agentic RAG Setup"
echo "================================"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "ℹ️  Creating .env file from template..."
    cp .env.example .env
    echo "📝 Please edit .env file and add your API keys:"
    echo "   - OPENAI_API_KEY"
    echo "   - GEMINI_API_KEY"
    echo ""
    read -p "Press Enter to continue after updating .env file..."
fi

echo "🔨 Building Docker images..."
docker compose build

if [ $? -ne 0 ]; then
    echo "❌ Build failed"
    exit 1
fi

echo "✅ Build successful"
echo ""

echo "🚀 Starting services..."
docker compose up -d

if [ $? -ne 0 ]; then
    echo "❌ Failed to start services"
    exit 1
fi

echo "✅ Services started successfully"
echo ""

echo "⏳ Waiting for services to be ready..."
sleep 5

# Check backend health
echo "🔍 Checking backend health..."
for i in {1..30}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ Backend is healthy"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "⚠️  Backend health check timeout"
    fi
    sleep 1
done

echo ""
echo "🎉 Setup complete!"
echo ""
echo "📍 Access the application:"
echo "   Frontend: http://localhost:3000"
echo "   Backend:  http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "📋 Useful commands:"
echo "   View logs:    docker compose logs -f"
echo "   Stop:         docker compose down"
echo "   Restart:      docker compose restart"
echo "   Clear data:   docker compose down -v"
echo ""
