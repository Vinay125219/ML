#!/bin/bash
set -e

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check for Docker
if ! command_exists docker; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check for Docker Compose
if ! command_exists docker-compose; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "🚀 Starting MLOps Housing Pipeline"

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p models data housinglogs mlruns

# Set environment variables
export DOCKER_USERNAME=${DOCKER_USERNAME:-ramya5870}
export TAG=${TAG:-latest}

# Stop any existing containers
echo "🛑 Stopping existing containers..."
docker-compose -f docker-compose.monitoring.yml down 2>/dev/null || true

# Pull the latest images
echo "📥 Pulling latest images..."
docker pull ${DOCKER_USERNAME}/mlops-housing-pipeline:${TAG}
docker pull prom/prometheus:latest
docker pull grafana/grafana:latest
docker pull python:3.10-slim

# Start services
echo "🚀 Starting services..."
docker-compose -f docker-compose.monitoring.yml up -d

# Wait for services to be ready
echo "⏳ Waiting for services to initialize..."
sleep 30

# Check service health
echo "🏥 Checking service health..."
SERVICES_OK=true

# Check Housing API
if ! curl -s http://localhost:8000/docs > /dev/null; then
    echo "❌ Housing API is not responding"
    SERVICES_OK=false
fi

# Check Prometheus
if ! curl -s http://localhost:9090/-/healthy > /dev/null; then
    echo "❌ Prometheus is not responding"
    SERVICES_OK=false
fi

# Check Grafana
if ! curl -s http://localhost:3001/api/health > /dev/null; then
    echo "❌ Grafana is not responding"
    SERVICES_OK=false
fi

# Check MLflow
if ! curl -s http://localhost:5000 > /dev/null; then
    echo "❌ MLflow is not responding"
    SERVICES_OK=false
fi

if [ "$SERVICES_OK" = true ]; then
    echo "✅ All services are running!"
    echo ""
    echo "🌐 Access your services at:"
    echo "  - Housing API:  http://localhost:8000/docs"
    echo "  - Prometheus:   http://localhost:9090"
    echo "  - Grafana:     http://localhost:3001 (admin/admin)"
    echo "  - MLflow:      http://localhost:5000"
else
    echo "⚠️ Some services failed to start. Check the logs:"
    echo "  docker-compose -f docker-compose.monitoring.yml logs"
fi
