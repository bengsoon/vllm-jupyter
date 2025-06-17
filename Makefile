# Makefile for vLLM + Jupyter Docker Compose Project

# Detect Docker Compose command (try new syntax first, then legacy)
DOCKER_COMPOSE := $(shell if docker compose version >/dev/null 2>&1; then echo "docker compose"; else echo "docker-compose"; fi)

.PHONY: help build up down restart logs clean test dev-up dev-down status

# Default target
help:
	@echo "🚀 vLLM + Jupyter Docker Compose Project"
	@echo "========================================"
	@echo ""
	@echo "Using Docker Compose command: $(DOCKER_COMPOSE)"
	@echo ""
	@echo "Available commands:"
	@echo "  help        Show this help message"
	@echo "  build       Build the Docker images"
	@echo "  up          Start all services"
	@echo "  down        Stop all services"
	@echo "  restart     Restart all services"
	@echo "  logs        Show logs for all services"
	@echo "  clean       Clean up Docker resources"
	@echo "  test        Test API connectivity"
	@echo "  dev-up      Start services in development mode"
	@echo "  dev-down    Stop development services"
	@echo "  status      Show service status"
	@echo "  jupyter-list List running Jupyter servers in the container"
	@echo ""
	@echo "Service-specific commands:"
	@echo "  logs-vllm   Show vLLM server logs"
	@echo "  logs-jupyter Show Jupyter Lab logs"
	@echo ""
	@echo "Development commands:"
	@echo "  shell-jupyter  Open shell in Jupyter container"
	@echo "  install-deps   Install additional dependencies"

# Build Docker images
build:
	@echo "🔨 Building Docker images..."
	$(DOCKER_COMPOSE) build

# Start all services
up:
	@echo "🚀 Starting all services..."
	./start.sh

# Stop all services
down:
	@echo "🛑 Stopping all services..."
	$(DOCKER_COMPOSE) down

# Restart all services
restart:
	@echo "🔄 Restarting all services..."
	$(DOCKER_COMPOSE) restart

# Show logs for all services
logs:
	@echo "📋 Showing logs for all services..."
	$(DOCKER_COMPOSE) logs -f

# Show logs for vLLM server only
logs-vllm:
	@echo "📋 Showing vLLM server logs..."
	$(DOCKER_COMPOSE) logs -f vllm-server

# Show logs for Jupyter Lab only
logs-jupyter:
	@echo "📋 Showing Jupyter Lab logs..."
	$(DOCKER_COMPOSE) logs -f jupyter-lab

# Clean up Docker resources
clean:
	@echo "🧹 Cleaning up Docker resources..."
	$(DOCKER_COMPOSE) down -v --remove-orphans
	docker system prune -f
	docker volume prune -f

# Test API connectivity
test:
	@echo "🧪 Testing vLLM API connectivity..."
	python3 test_vllm_api.py

# Start services in development mode
dev-up:
	@echo "🔧 Starting services in development mode..."
	$(DOCKER_COMPOSE) -f docker-compose.yml -f docker-compose.dev.yml up -d
	@echo "✅ Development services started!"
	@echo "   📓 Jupyter Lab: http://localhost:8888/?token=dev-token"
	@echo "   🎯 vLLM API: http://localhost:8000 (API key: dev-api-key)"

# Stop development services
dev-down:
	@echo "🛑 Stopping development services..."
	$(DOCKER_COMPOSE) -f docker-compose.yml -f docker-compose.dev.yml down

# Show service status
status:
	@echo "📊 Service status:"
	$(DOCKER_COMPOSE) ps

# Open shell in Jupyter container
shell-jupyter:
	@echo "🐚 Opening shell in Jupyter container..."
	$(DOCKER_COMPOSE) exec jupyter-lab bash

# List running Jupyter servers in the container
jupyter-list:
	@echo "🔍 Listing running Jupyter servers in the container..."
	$(DOCKER_COMPOSE) exec jupyter-lab jupyter server list

# Install additional dependencies in Jupyter container
install-deps:
	@echo "📦 Installing additional dependencies with uv (fast!)..."
	@read -p "Enter package names (space-separated): " packages; \
	$(DOCKER_COMPOSE) exec jupyter-lab uv pip install --system $$packages

# Pull latest images
pull:
	@echo "⬇️ Pulling latest images..."
	$(DOCKER_COMPOSE) pull

# Update and restart services
update: pull build restart
	@echo "🔄 Services updated and restarted!"

# Backup data
backup:
	@echo "💾 Creating backup of data and notebooks..."
	tar -czf backup_$(shell date +%Y%m%d_%H%M%S).tar.gz notebooks/ data/ models/
	@echo "✅ Backup created!"

# Monitor resources
monitor:
	@echo "📊 Monitoring Docker resources..."
	watch -n 2 'docker stats --no-stream'

# Quick development setup
dev-setup: build dev-up
	@echo "🎉 Development environment ready!"
	@sleep 5
	@make test
