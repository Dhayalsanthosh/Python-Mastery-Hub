# Python Mastery Hub - Makefile for project automation
# This Makefile provides convenient commands for development, testing, and deployment

.PHONY: help install install-dev test test-cov lint format type-check security docs clean build publish docker run-cli run-web

# Default target
help: ## Show this help message
	@echo "Python Mastery Hub - Development Commands"
	@echo "========================================"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "%-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# Installation targets
install: ## Install production dependencies
	poetry install --only=main

install-dev: ## Install all dependencies including development tools
	poetry install
	poetry run pre-commit install

# Testing targets
test: ## Run tests with pytest
	poetry run pytest tests/ -v --tb=short

test-cov: ## Run tests with coverage report
	poetry run pytest tests/ -v --cov=src --cov-report=html --cov-report=term-missing

test-cov-xml: ## Run tests with XML coverage report (for CI)
	poetry run pytest tests/ --cov=src --cov-report=xml

test-integration: ## Run integration tests only
	poetry run pytest tests/ -v -m integration

test-unit: ## Run unit tests only
	poetry run pytest tests/ -v -m "not integration"

test-watch: ## Run tests in watch mode
	poetry run ptw tests/ -- -v

# Code quality targets
lint: ## Run all linting tools
	poetry run flake8 src tests
	poetry run pylint src tests
	poetry run bandit -r src

format: ## Format code with black and isort
	poetry run black src tests
	poetry run isort src tests

format-check: ## Check if code is properly formatted
	poetry run black --check src tests
	poetry run isort --check-only src tests

type-check: ## Run type checking with mypy
	poetry run mypy src

security: ## Run security checks
	poetry run bandit -r src
	poetry run safety check

pre-commit: ## Run pre-commit hooks on all files
	poetry run pre-commit run --all-files

# Documentation targets
docs: ## Build documentation with Sphinx
	cd docs && poetry run make html

docs-serve: ## Serve documentation locally
	cd docs/_build/html && python -m http.server 8080

docs-clean: ## Clean documentation build
	cd docs && poetry run make clean

# Build and package targets
clean: ## Clean build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete

build: clean ## Build package
	poetry build

publish: build ## Publish to PyPI
	poetry publish

publish-test: build ## Publish to TestPyPI
	poetry publish --repository testpypi

# Docker targets
docker-build: ## Build Docker image
	docker build -t python-mastery-hub .

docker-run: ## Run Docker container
	docker run -p 8000:8000 python-mastery-hub

docker-dev: ## Run Docker container in development mode
	docker run -p 8000:8000 -v $(PWD):/app python-mastery-hub

# Application targets
run-cli: ## Run CLI interface
	poetry run python -m python_mastery_hub.cli.main

run-web: ## Run web server
	poetry run python -m python_mastery_hub.web.app

run-web-dev: ## Run web server in development mode
	poetry run uvicorn python_mastery_hub.web.app:app --reload --host 0.0.0.0 --port 8000

# Development targets
dev-setup: install-dev ## Setup development environment
	@echo "Development environment setup complete!"
	@echo "Run 'make run-cli' to start the CLI interface"
	@echo "Run 'make run-web' to start the web server"

check-all: format-check lint type-check security test ## Run all checks (CI pipeline)

demo: ## Run a quick demo
	poetry run python -c "from python_mastery_hub.core import get_module; m = get_module('basics'); print('Demo:', m.demonstrate('variables')['explanation'])"

# Database and migration targets (for future use)
migrate: ## Run database migrations
	@echo "Database migrations not yet implemented"

migrate-test: ## Run migrations on test database
	@echo "Test database migrations not yet implemented"

# Performance and benchmarking targets
benchmark: ## Run performance benchmarks
	poetry run pytest tests/test_benchmarks.py -v --benchmark-only

profile: ## Run profiling on key components
	poetry run python -m cProfile -s cumulative -m python_mastery_hub.cli.main --help

# Release targets
version-patch: ## Bump patch version
	poetry version patch

version-minor: ## Bump minor version
	poetry version minor

version-major: ## Bump major version
	poetry version major

release-patch: version-patch build publish ## Create patch release
	git add pyproject.toml
	git commit -m "Bump version to $(shell poetry version -s)"
	git tag v$(shell poetry version -s)
	git push origin main --tags

release-minor: version-minor build publish ## Create minor release
	git add pyproject.toml
	git commit -m "Bump version to $(shell poetry version -s)"
	git tag v$(shell poetry version -s)
	git push origin main --tags

# Environment management
env-info: ## Show environment information
	@echo "Python version: $(shell python --version)"
	@echo "Poetry version: $(shell poetry --version)"
	@echo "Current environment: $(shell poetry env info --path)"
	@echo "Dependencies:"
	@poetry show --tree

env-update: ## Update dependencies
	poetry update

env-lock: ## Lock dependencies
	poetry lock

# Code analysis targets
complexity: ## Analyze code complexity
	poetry run radon cc src --show-complexity

metrics: ## Show code metrics
	poetry run radon mi src
	poetry run radon hal src

# Documentation and examples
examples: ## Run all example code
	@echo "Running example demonstrations..."
	poetry run python -c "
from python_mastery_hub.core import list_modules, get_module
for module_info in list_modules():
    print(f'Testing {module_info[\"name\"]}...')
    module = get_module(module_info['name'].lower().replace(' ', '_').replace('&', '').replace('__', '_'))
    for topic in module.get_topics()[:1]:  # Test first topic only for speed
        demo = module.demonstrate(topic)
        print(f'  ✓ {topic}: {len(demo[\"examples\"])} examples')
print('All examples working!')
"

# IDE and editor support
vscode-setup: ## Setup VSCode configuration
	mkdir -p .vscode
	cat > .vscode/settings.json << 'EOF'
{
    "python.defaultInterpreterPath": ".venv/bin/python",
    "python.formatting.provider": "black",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.linting.mypyEnabled": true,
    "python.testing.pytestEnabled": true,
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    }
}
EOF
	@echo "VSCode settings created"

# Monitoring and health checks
health-check: ## Run health checks on the application
	@echo "Running health checks..."
	poetry run python -c "
import sys
sys.path.insert(0, 'src')
from python_mastery_hub.core import MODULE_REGISTRY, get_module
print(f'✓ {len(MODULE_REGISTRY)} modules registered')
for name in MODULE_REGISTRY:
    module = get_module(name)
    topics = module.get_topics()
    print(f'✓ {name}: {len(topics)} topics available')
print('Health check passed!')
"

# Quick start target
quickstart: install-dev check-all ## Quick setup and validation
	@echo ""
	@echo "🎉 Python Mastery Hub is ready!"
	@echo ""
	@echo "Quick commands:"
	@echo "  make run-cli       - Start interactive CLI"
	@echo "  make run-web       - Start web interface"
	@echo "  make test          - Run tests"
	@echo "  make demo          - Quick demo"
	@echo ""

# CI/CD targets
ci-test: ## Run CI test suite
	poetry run pytest tests/ -v --cov=src --cov-report=xml --junitxml=test-results.xml

ci-build: clean format-check lint type-check security ci-test build ## Full CI pipeline

cd-deploy: ## Deploy to production (placeholder)
	@echo "Deployment pipeline not yet implemented"

# Advanced targets
stress-test: ## Run stress tests
	poetry run python -c "
import time
from python_mastery_hub.core import get_module
print('Running stress test...')
start = time.time()
for i in range(100):
    module = get_module('basics')
    demo = module.demonstrate('variables')
    if i % 20 == 0:
        print(f'  Iteration {i}: OK')
end = time.time()
print(f'Stress test completed in {end-start:.2f}s')
"

memory-test: ## Test memory usage
	poetry run python -c "
import psutil
import os
from python_mastery_hub.core import get_module
process = psutil.Process(os.getpid())
initial_memory = process.memory_info().rss / 1024 / 1024
print(f'Initial memory: {initial_memory:.1f} MB')
modules = []
for i in range(10):
    modules.append(get_module('basics'))
final_memory = process.memory_info().rss / 1024 / 1024
print(f'Final memory: {final_memory:.1f} MB')
print(f'Memory increase: {final_memory - initial_memory:.1f} MB')
"

# Help target should be first when no target is specified
.DEFAULT_GOAL := help