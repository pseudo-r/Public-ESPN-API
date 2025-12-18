.PHONY: help install dev test lint format migrate run shell docker-up docker-down docker-build clean celery beat

# Default target
help:
	@echo "ESPN Service - Available Commands"
	@echo ""
	@echo "Development:"
	@echo "  install     Install production dependencies"
	@echo "  dev         Install development dependencies"
	@echo "  run         Run development server"
	@echo "  shell       Open Django shell"
	@echo "  migrate     Run database migrations"
	@echo ""
	@echo "Testing:"
	@echo "  test        Run all tests"
	@echo "  test-cov    Run tests with coverage report"
	@echo "  test-fast   Run tests without coverage"
	@echo ""
	@echo "Code Quality:"
	@echo "  lint        Run linter (ruff)"
	@echo "  format      Format code (ruff)"
	@echo "  typecheck   Run type checker (mypy)"
	@echo "  pre-commit  Run pre-commit hooks"
	@echo ""
	@echo "Docker:"
	@echo "  docker-up   Start all services"
	@echo "  docker-down Stop all services"
	@echo "  docker-build Build Docker images"
	@echo "  docker-logs View logs"
	@echo ""
	@echo "Celery:"
	@echo "  celery      Start Celery worker"
	@echo "  beat        Start Celery beat scheduler"
	@echo ""
	@echo "Data:"
	@echo "  ingest-teams   Ingest teams (SPORT=basketball LEAGUE=nba)"
	@echo "  ingest-scores  Ingest scoreboard (SPORT=basketball LEAGUE=nba DATE=20241215)"

# Installation
install:
	pip install -e .

dev:
	pip install -e ".[dev]"
	pre-commit install

# Development
run:
	python manage.py runserver

shell:
	python manage.py shell

migrate:
	python manage.py makemigrations
	python manage.py migrate

createsuperuser:
	python manage.py createsuperuser

collectstatic:
	python manage.py collectstatic --noinput

# Testing
test:
	pytest

test-cov:
	pytest --cov=apps --cov=clients --cov-report=html --cov-report=term-missing

test-fast:
	pytest --no-cov -x

# Code Quality
lint:
	ruff check .

format:
	ruff format .
	ruff check --fix .

typecheck:
	mypy apps clients

pre-commit:
	pre-commit run --all-files

# Docker
docker-up:
	docker compose up -d

docker-down:
	docker compose down

docker-build:
	docker compose build

docker-logs:
	docker compose logs -f

docker-shell:
	docker compose exec web bash

docker-test:
	docker compose exec web pytest

# Celery
celery:
	celery -A config worker -l INFO

beat:
	celery -A config beat -l INFO

# Data Ingestion
SPORT ?= basketball
LEAGUE ?= nba
DATE ?= $(shell date +%Y%m%d)

ingest-teams:
	python manage.py ingest_teams $(SPORT) $(LEAGUE)

ingest-scores:
	python manage.py ingest_scoreboard $(SPORT) $(LEAGUE) --date=$(DATE)

# Cleanup
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	find . -type d -name "htmlcov" -exec rm -rf {} +
	find . -type f -name ".coverage" -delete
	rm -rf dist/ build/ *.egg-info/
