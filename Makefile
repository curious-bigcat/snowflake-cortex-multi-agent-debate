# Multi-Agent Debate System - Makefile
# Convenience commands for Docker operations

.PHONY: build run stop logs shell cli clean help

# Default target
help:
	@echo "Multi-Agent Debate System - Docker Commands"
	@echo ""
	@echo "Usage:"
	@echo "  make build     - Build Docker images"
	@echo "  make run       - Start the Streamlit app"
	@echo "  make stop      - Stop all containers"
	@echo "  make logs      - View container logs"
	@echo "  make shell     - Open shell in running container"
	@echo "  make cli       - Run CLI command (use CMD='run NVDA')"
	@echo "  make clean     - Remove containers and images"
	@echo "  make dev       - Run with hot reload (mount source)"
	@echo ""
	@echo "Examples:"
	@echo "  make run                    # Start Streamlit app at http://localhost:8501"
	@echo "  make cli CMD='run NVDA'     # Run debate for NVDA"
	@echo "  make cli CMD='search AAPL'  # Search for AAPL"

# Build Docker images
build:
	docker-compose build

# Run the Streamlit app
run:
	docker-compose up -d debate-app
	@echo ""
	@echo "Streamlit app starting at http://localhost:8501"
	@echo "Use 'make logs' to view logs"
	@echo "Use 'make stop' to stop the app"

# Run with hot reload for development
dev:
	docker-compose run --rm -p 8501:8501 \
		-v $(PWD):/app \
		debate-app

# Stop all containers
stop:
	docker-compose down

# View logs
logs:
	docker-compose logs -f debate-app

# Open shell in running container
shell:
	docker-compose exec debate-app /bin/bash

# Run CLI commands
# Usage: make cli CMD='run NVDA --rounds 2'
cli:
	docker-compose run --rm debate-cli $(CMD)

# Clean up containers and images
clean:
	docker-compose down --rmi local -v
	@echo "Cleaned up containers and images"

# Rebuild and run
rebuild: clean build run
