.PHONY: help install dev test fmt check start start-web start-mlflow clean

# Use uv from PATH or home directory
UV := $(shell command -v uv 2>/dev/null || echo "$(HOME)/.local/bin/uv")

# Default target
help:
	@echo "Usage: make [target]"
	@echo ""
	@echo "Setup:"
	@echo "  install     Install dependencies"
	@echo "  dev         Install dev dependencies"
	@echo ""
	@echo "Development:"
	@echo "  start       Start all services (web, mlflow, pi)"
	@echo "  start-web   Start only the web server"
	@echo "  start-mlflow Start only MLflow server"
	@echo ""
	@echo "Testing & Quality:"
	@echo "  test        Run all tests (verbose)"
	@echo "  fmt         Format and lint code (ruff)"
	@echo "  check       Run tests + fmt"
	@echo ""
	@echo "Maintenance:"
	@echo "  clean       Remove generated files"

# Setup
install:
	$(UV) sync

dev:
	$(UV) sync --dev

# Development
start:
	$(UV) run honcho start

start-web:
	$(UV) run uvicorn backend.main:app --reload --port 8000

start-mlflow:
	$(UV) run mlflow server --host 127.0.0.1 --port 5000

# Testing & Quality
test:
	$(UV) run pytest -v

fmt:
	$(UV) run ruff format .
	$(UV) run ruff check --fix .

check: test fmt

# Maintenance
clean:
	rm -rf .venv
	rm -rf .pytest_cache
	rm -rf .ruff_cache
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
