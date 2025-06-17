#!/bin/bash

# Quick package installation script using uv in the Jupyter container

if [ $# -eq 0 ]; then
    echo "Usage: $0 <package1> [package2] [package3] ..."
    echo "Example: $0 matplotlib seaborn plotly"
    exit 1
fi

# Detect Docker Compose command
if docker compose version >/dev/null 2>&1; then
    DOCKER_COMPOSE_CMD="docker compose"
elif command -v docker-compose >/dev/null 2>&1; then
    DOCKER_COMPOSE_CMD="docker-compose"
else
    echo "❌ Docker Compose not found"
    exit 1
fi

echo "🚀 Installing packages with uv (lightning fast!)..."
echo "📦 Packages: $*"

# Install packages using uv
$DOCKER_COMPOSE_CMD exec jupyter-lab uv pip install --system "$@"

if [ $? -eq 0 ]; then
    echo "✅ Packages installed successfully!"
    echo "💡 Restart your Jupyter kernel to use the new packages"
else
    echo "❌ Package installation failed"
    exit 1
fi
