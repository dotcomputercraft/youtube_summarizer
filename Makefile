# YouTube Video Summarizer - Makefile

.PHONY: help install install-dev test test-coverage clean lint format type-check run-example

# Default target
help:
	@echo "YouTube Video Summarizer - Available commands:"
	@echo ""
	@echo "Setup:"
	@echo "  install      Install production dependencies"
	@echo "  install-dev  Install development dependencies"
	@echo ""
	@echo "Testing:"
	@echo "  test         Run all tests"
	@echo "  test-coverage Run tests with coverage report"
	@echo "  test-unit    Run only unit tests"
	@echo ""
	@echo "Code Quality:"
	@echo "  lint         Run flake8 linting"
	@echo "  format       Format code with black"
	@echo "  type-check   Run mypy type checking"
	@echo "  quality      Run all quality checks"
	@echo ""
	@echo "Usage:"
	@echo "  run-example  Run example summarization"
	@echo "  demo         Run demo with sample video"
	@echo ""
	@echo "Maintenance:"
	@echo "  clean        Clean up generated files"
	@echo "  docs         Generate documentation"

# Installation
install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements.txt
	pip install pytest pytest-cov pytest-mock black flake8 mypy

# Testing
test:
	python -m pytest tests/ -v

test-coverage:
	python -m pytest tests/ --cov=src --cov-report=html --cov-report=term-missing

test-unit:
	python -m pytest tests/ -m "not integration" -v

# Code Quality
lint:
	flake8 src/ tests/ --max-line-length=100 --ignore=E203,W503

format:
	black src/ tests/ --line-length=100

type-check:
	mypy src/ --ignore-missing-imports

quality: lint type-check
	@echo "All quality checks passed!"

# Usage Examples
run-example:
	@echo "Running example summarization..."
	@echo "Note: Set OPENAI_API_KEY environment variable first"
	./yt-summarizer summarize "https://youtube.com/watch?v=dQw4w9WgXcQ" --style brief

demo:
	@echo "YouTube Video Summarizer Demo"
	@echo "=============================="
	@echo ""
	@echo "1. Checking configuration..."
	./yt-summarizer config-info
	@echo ""
	@echo "2. Getting video info..."
	./yt-summarizer info "dQw4w9WgXcQ"
	@echo ""
	@echo "3. Extracting transcript..."
	./yt-summarizer extract "dQw4w9WgXcQ" --format text | head -10
	@echo ""
	@echo "4. Generating summary..."
	./yt-summarizer summarize "dQw4w9WgXcQ" --style brief

# Maintenance
clean:
	rm -rf __pycache__/
	rm -rf src/__pycache__/
	rm -rf tests/__pycache__/
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf *.egg-info/
	rm -rf build/
	rm -rf dist/
	find . -name "*.pyc" -delete
	find . -name "*.pyo" -delete

docs:
	@echo "Documentation files:"
	@echo "- README.md: Main documentation"
	@echo "- USAGE.md: Detailed usage guide"
	@echo "- API documentation in source files"

# Development workflow
dev-setup: install-dev
	@echo "Development environment setup complete!"
	@echo "Don't forget to set your OPENAI_API_KEY environment variable"

# CI/CD targets
ci-test: test-coverage lint type-check
	@echo "CI tests completed successfully!"

# Package building
build:
	python setup.py sdist bdist_wheel

# Installation from source
install-local:
	pip install -e .

# Help for specific commands
help-commands:
	@echo "Available CLI commands:"
	./yt-summarizer --help

