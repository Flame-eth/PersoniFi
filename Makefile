.PHONY: help setup build up down logs migrate createsuperuser test test-cov test-performance lint format shell bash db-shell redis-shell clean docs

help:
	@echo "PersoniFi Development Commands"
	@echo "==============================="
	@echo "setup              Setup project with Docker Compose"
	@echo "build              Build Docker images"
	@echo "up                 Start services"
	@echo "down               Stop services"
	@echo "logs               View service logs"
	@echo "migrate            Run database migrations"
	@echo "createsuperuser    Create Django superuser"
	@echo "test               Run all tests"
	@echo "test-cov           Run tests with coverage report"
	@echo "test-performance   Run performance benchmarks"
	@echo "lint               Run code linting (pylint)"
	@echo "format             Format code (black, isort)"
	@echo "shell              Django shell"
	@echo "bash               Bash shell in web container"
	@echo "db-shell           PostgreSQL shell"
	@echo "redis-shell        Redis CLI"
	@echo "clean              Clean up Docker volumes and containers"
	@echo "docs               Generate documentation"

setup:
	@bash setup.sh

build:
	docker-compose build

up:
	docker-compose up -d
	@echo "Services started. Access at http://localhost:8000"

down:
	docker-compose down

logs:
	docker-compose logs -f

migrate:
	docker-compose exec web python manage.py migrate

createsuperuser:
	docker-compose exec web python manage.py createsuperuser

test:
	pytest tests/ -v

test-cov:
	pytest tests/ -v --cov=apps --cov-report=html --cov-report=term --cov-fail-under=80
	@echo "Coverage report generated in htmlcov/"

test-performance:
	pytest tests/performance/ -v --benchmark-only

test-rest:
	pytest tests/apps/api_rest.py -v -m rest

test-graphql:
	pytest tests/apps/api_graphql.py -v -m graphql

test-unit:
	pytest tests/apps/ -v --ignore=tests/apps/api_rest.py --ignore=tests/apps/api_graphql.py

lint:
	pylint apps/ config/ || true

format:
	black apps/ config/ tests/
	isort apps/ config/ tests/

shell:
	docker-compose exec web python manage.py shell

bash:
	docker-compose exec web bash

db-shell:
	docker-compose exec db psql -U personifi -d personifi

redis-shell:
	docker-compose exec redis redis-cli

clean:
	docker-compose down -v
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .coverage

docs:
	@echo "Documentation files:"
	@echo "  - README.md"
	@echo "  - DEPLOYMENT.md"
	@echo "  - TESTING.md"
	@echo "  - ARCHITECTURE_DECISIONS.md"

# Development shortcuts
dev-test:
	@make test

dev-logs:
	docker-compose logs -f web

dev-migrate:
	@make migrate

# CI/CD simulation
ci: lint test test-cov
	@echo "✅ CI checks passed"

# Database backup
db-backup:
	docker-compose exec db pg_dump -U personifi personifi > backup_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "Database backup created"

# Database restore
db-restore:
	@read -p "Enter backup filename: " backup; \
	docker-compose exec -T db psql -U personifi personifi < $$backup
	@echo "Database restored"

# Install dependencies
install:
	pip install -r requirements/development.txt

# Initialize project
init: setup migrate createsuperuser
	@echo "✅ Project initialized"
