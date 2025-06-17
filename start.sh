#!/bin/bash

# vLLM + Jupyter Docker Compose Startup Script

set -e

echo "🚀 Starting vLLM + Jupyter Lab Docker Compose Project"
echo "=================================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check if Docker Compose is available (try both new and legacy syntax)
DOCKER_COMPOSE_CMD=""
if docker compose version > /dev/null 2>&1; then
    DOCKER_COMPOSE_CMD="docker compose"
    echo "✅ Docker Compose found (using 'docker compose')"
elif command -v docker-compose > /dev/null 2>&1; then
    DOCKER_COMPOSE_CMD="docker-compose"
    echo "✅ Docker Compose found (using 'docker-compose')"
else
    echo "❌ Docker Compose is not available. Please install Docker Compose or Docker Desktop."
    exit 1
fi

# Check for NVIDIA GPU support if requested
if grep -q "nvidia" docker-compose.yml; then
    echo "🔍 Checking NVIDIA GPU support..."
    if ! command -v nvidia-smi > /dev/null 2>&1; then
        echo "⚠️  NVIDIA drivers not found. GPU acceleration may not work."
    else
        echo "✅ NVIDIA GPU detected:"
        nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
    fi
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p models data notebooks vllm-cache

# Check if .env file exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file to set your configuration before starting services."
    echo "   - Set secure API keys and tokens"
    echo "   - Configure model settings"
    echo "   - Adjust resource limits"
fi

# Function to check if a service is ready
check_service_health() {
    local service_name=$1
    local health_url=$2
    local max_attempts=30
    local attempt=1

    echo "🔍 Checking $service_name health..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s -f "$health_url" > /dev/null 2>&1; then
            echo "✅ $service_name is ready!"
            return 0
        fi
        
        echo "   Attempt $attempt/$max_attempts: Waiting for $service_name..."
        sleep 10
        attempt=$((attempt + 1))
    done
    
    echo "❌ $service_name failed to start within expected time"
    return 1
}

# Start services
echo "🐳 Starting Docker Compose services..."
$DOCKER_COMPOSE_CMD up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 5

# Check vLLM server health
if check_service_health "vLLM Server" "http://localhost:8000/health"; then
    echo "🎯 vLLM Server is accessible at: http://localhost:8000"
    echo "   📖 API Documentation: http://localhost:8000/docs"
else
    echo "⚠️  vLLM Server may not be ready yet. Check logs with: $DOCKER_COMPOSE_CMD logs vllm-server"
fi

# Check Jupyter Lab
if check_service_health "Jupyter Lab" "http://localhost:8888"; then
    echo "📓 Jupyter Lab is accessible at: http://localhost:8888"
    
    # Try to extract the token from the container logs
    echo "🔑 Getting Jupyter Lab access token..."
    sleep 2
    token=$($DOCKER_COMPOSE_CMD logs jupyter-lab 2>/dev/null | grep -oP 'token=\K[a-f0-9]+' | head -1)
    if [ -n "$token" ]; then
        echo "   🎫 Access URL: http://localhost:8888/?token=$token"
    else
        echo "   🎫 Use the token configured in your .env file"
    fi
else
    echo "⚠️  Jupyter Lab may not be ready yet. Check logs with: $DOCKER_COMPOSE_CMD logs jupyter-lab"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "📋 Next steps:"
echo "   1. Open Jupyter Lab and try the example notebook: vllm_batched_inference_example.ipynb"
echo "   2. Test the vLLM API with curl or your favorite HTTP client"
echo "   3. Customize the configuration in docker-compose.yml as needed"
echo ""
echo "🔧 Useful commands:"
echo "   - View logs: $DOCKER_COMPOSE_CMD logs -f [service-name]"
echo "   - Stop services: $DOCKER_COMPOSE_CMD down"
echo "   - Rebuild: $DOCKER_COMPOSE_CMD build"
echo "   - Update: $DOCKER_COMPOSE_CMD pull && $DOCKER_COMPOSE_CMD up -d"
echo ""
echo "📊 Monitor resources:"
echo "   - docker stats"
echo "   - nvidia-smi (for GPU usage)"
