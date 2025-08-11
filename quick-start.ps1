# Function to check if command exists
function Test-Command {
    param($Command)
    $oldPreference = $ErrorActionPreference
    $ErrorActionPreference = 'stop'
    try {
        if (Get-Command $Command) { return $true }
    } catch {
        return $false
    } finally {
        $ErrorActionPreference = $oldPreference
    }
}

# Check for Docker
if (-not (Test-Command docker)) {
    Write-Host "❌ Docker is not installed. Please install Docker first."
    exit 1
}

# Check for Docker Compose
if (-not (Test-Command docker-compose)) {
    Write-Host "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
}

Write-Host "🚀 Starting MLOps Housing Pipeline"

# Create necessary directories
Write-Host "📁 Creating necessary directories..."
New-Item -ItemType Directory -Force -Path models, data, housinglogs, mlruns | Out-Null

# Set environment variables
$env:DOCKER_USERNAME = if ($env:DOCKER_USERNAME) { $env:DOCKER_USERNAME } else { "ramya5870" }
$env:TAG = if ($env:TAG) { $env:TAG } else { "latest" }

# Stop any existing containers
Write-Host "🛑 Stopping existing containers..."
docker-compose -f docker-compose.monitoring.yml down 2>$null

# Pull the latest images
Write-Host "📥 Pulling latest images..."
docker pull ${env:DOCKER_USERNAME}/mlops-housing-pipeline:${env:TAG}
docker pull prom/prometheus:latest
docker pull grafana/grafana:latest
docker pull python:3.10-slim

# Start services
Write-Host "🚀 Starting services..."
docker-compose -f docker-compose.monitoring.yml up -d

# Wait for services to be ready
Write-Host "⏳ Waiting for services to initialize..."
Start-Sleep -Seconds 30

# Check service health
Write-Host "🏥 Checking service health..."
$servicesOk = $true

# Check Housing API
try {
    Invoke-WebRequest -Uri http://localhost:8000/docs -UseBasicParsing | Out-Null
} catch {
    Write-Host "❌ Housing API is not responding"
    $servicesOk = $false
}

# Check Prometheus
try {
    Invoke-WebRequest -Uri http://localhost:9090/-/healthy -UseBasicParsing | Out-Null
} catch {
    Write-Host "❌ Prometheus is not responding"
    $servicesOk = $false
}

# Check Grafana
try {
    Invoke-WebRequest -Uri http://localhost:3001/api/health -UseBasicParsing | Out-Null
} catch {
    Write-Host "❌ Grafana is not responding"
    $servicesOk = $false
}

# Check MLflow
try {
    Invoke-WebRequest -Uri http://localhost:5000 -UseBasicParsing | Out-Null
} catch {
    Write-Host "❌ MLflow is not responding"
    $servicesOk = $false
}

if ($servicesOk) {
    Write-Host "`n✅ All services are running!"
    Write-Host "`n🌐 Access your services at:"
    Write-Host "  - Housing API:  http://localhost:8000/docs"
    Write-Host "  - Prometheus:   http://localhost:9090"
    Write-Host "  - Grafana:     http://localhost:3001 (admin/admin)"
    Write-Host "  - MLflow:      http://localhost:5000"
} else {
    Write-Host "`n⚠️ Some services failed to start. Check the logs:"
    Write-Host "  docker-compose -f docker-compose.monitoring.yml logs"
}
