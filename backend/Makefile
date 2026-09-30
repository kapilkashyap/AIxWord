.PHONY: help install install-dev test test-cov lint format type-check clean run

help:
	@echo "AIxWord Backend - Development Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make install      Install package dependencies"
	@echo "  make install-dev  Install package + dev dependencies"
	@echo ""
	@echo "Development:"
	@echo "  make run          Start development server"
	@echo "  make test         Run tests"
	@echo "  make test-cov     Run tests with coverage report"
	@echo "  make lint         Run linter (ruff)"
	@echo "  make format       Format code (black)"
	@echo "  make type-check   Run type checker (mypy)"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean        Remove build artifacts and cache"

install:
	pip install -e .

install-dev:
	pip install -e .
	pip install -r requirements-dev.txt

test:
	pytest

test-cov:
	pytest --cov=backend --cov-report=html --cov-report=term

lint:
	ruff check .

format:
	black .
	ruff check --fix .

type-check:
	mypy .

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache .mypy_cache .coverage htmlcov dist build

run:
	uvicorn backend.api.main:app --reload --host 0.0.0.0 --port 8000
