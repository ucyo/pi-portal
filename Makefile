.PHONY: help install dev test test-integ test-all fmt check start start-web clean
.PHONY: docker-build docker-up docker-down docker-logs docker-shell docker-clean

# Use uv from PATH or home directory
UV := $(shell command -v uv 2>/dev/null || echo "$(HOME)/.local/bin/uv")

# Default target
help:
	@echo "Usage: make [target]"
	@echo ""
	@echo "Setup:"
	@echo "  install       Install dependencies"
	@echo "  dev           Install dev dependencies"
	@echo ""
	@echo "Development:"
	@echo "  start         Start the web server (Pi managed by backend)"
	@echo ""
	@echo "Testing & Quality:"
	@echo "  test          Run unit tests (verbose)"
	@echo "  test-integ    Run integration tests (require Pi)"
	@echo "  test-all      Run all tests"
	@echo "  fmt           Format and lint code (ruff)"
	@echo "  check         Run unit tests + fmt"
	@echo ""
	@echo "Docker:"
	@echo "  docker-build  Build Docker image"
	@echo "  docker-up     Start services with Docker Compose"
	@echo "  docker-down   Stop services"
	@echo "  docker-logs   View logs"
	@echo "  docker-shell  Open shell in container"
	@echo "  docker-clean  Remove containers and volumes"
	@echo ""
	@echo "Maintenance:"
	@echo "  clean         Remove generated files"

# Setup
install:
	$(UV) sync

dev:
	$(UV) sync --dev

# Development
start:
	$(UV) run python -m backend.server

start-web: start

# Testing & Quality
test:
	$(UV) run pytest -v -m "not integration"

test-integ:
	$(UV) run pytest -v -m "integration"

test-all:
	$(UV) run pytest -v

fmt:
	$(UV) run ruff format .
	$(UV) run ruff check --fix .

check: test fmt

# Docker
docker-build:
	docker-compose build

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

docker-shell:
	docker-compose exec backend /bin/bash

docker-clean:
	docker-compose down -v
	docker rmi pi-portal:latest 2>/dev/null || true

# Maintenance
clean:
	rm -rf .venv
	rm -rf .pytest_cache
	rm -rf .ruff_cache
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
