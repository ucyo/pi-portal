.PHONY: help install dev test test-integ test-all fmt check start start-web clean

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
	@echo "  start       Start all services (web, pi)"
	@echo "  start-web   Start only the web server"
	@echo ""
	@echo "Testing & Quality:"
	@echo "  test        Run unit tests (verbose)"
	@echo "  test-integ  Run integration tests (require Pi)"
	@echo "  test-all    Run all tests"
	@echo "  fmt         Format and lint code (ruff)"
	@echo "  check       Run unit tests + fmt"
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
	$(UV) run uvicorn backend.main:app --reload --port 8000 --host 0.0.0.0

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

# Maintenance
clean:
	rm -rf .venv
	rm -rf .pytest_cache
	rm -rf .ruff_cache
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
