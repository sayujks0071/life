.PHONY: help install test format lint typecheck green clean

help:
	@echo "Available targets:"
	@echo "  install     - Install dependencies via poetry"
	@echo "  test        - Run pytest with coverage"
	@echo "  format      - Format code with black"
	@echo "  lint        - Lint code with ruff"
	@echo "  typecheck   - Type check with mypy"
	@echo "  green       - Run all checks (format, lint, typecheck, test)"
	@echo "  clean       - Remove generated files"

install:
	poetry install

test:
	poetry run pytest tests/ -v --cov=src/spinalmodes --cov-report=term-missing

format:
	poetry run black src/ tests/ tools/
	poetry run ruff --fix src/ tests/ tools/

lint:
	poetry run ruff check src/ tests/ tools/

typecheck:
	poetry run mypy src/ tests/ tools/ --ignore-missing-imports

green: format lint typecheck test
	@echo "✅ All checks passed!"

clean:
	rm -rf .pytest_cache .coverage htmlcov
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

