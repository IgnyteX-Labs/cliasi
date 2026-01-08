.PHONY: install test lint typecheck docs build clean all help

# Default target
all: lint typecheck test

help:
	@echo "Available targets:"
	@echo "  install    Install dependencies"
	@echo "  test       Run tests"
	@echo "  lint       Run lint checks"
	@echo "  typecheck  Run type checks"
	@echo "  docs       Build documentation"
	@echo "  build      Build the package"
	@echo "  clean      Remove build artifacts"
	@echo "  all        Run lint, typecheck, and test (default)"
	@echo "  help       Show this help message"

install:
	uv sync --group dev

test:
	uv run pytest

lint:
	uv run ruff check

typecheck:
	uv run mypy src

docs:
	uv run --group docs make html -C docs

build:
	uv build

clean:
	rm -rf dist/
	rm -rf docs/build/
	rm -rf .mypy_cache/
	rm -rf .pytest_cache/
	rm -rf .ruff_cache/
	find . -type d -name "__pycache__" -exec rm -rf {} +
