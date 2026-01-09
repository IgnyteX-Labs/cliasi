.PHONY: install test lint typecheck docs build clean all overwrite casts casts-clean cast-interactive aggconvert help

# Default target
all: lint typecheck test

help:
	@echo "Available targets:"
	@echo "  install    		Install dependencies"
	@echo "  test       		Run tests"
	@echo "  lint       		Run lint checks"
	@echo "  typecheck  		Run type checks"
	@echo "  docs       		Build documentation"
	@echo "  build      		Build the package"
	@echo "  clean      		Remove build artifacts"
	@echo "  all        		Run lint, typecheck, and test (default)"
	@echo "  casts      		Record asciinema casts for the documentation. Requires asciinema installed"
	@echo "  casts-clean 		Remove generated asciinema SVGs"
	@echo "  cast-interactive 	Record an interactive asciinema cast"
	@echo "  overwrite  		Flag to overwrite existing asciinema casts (used with 'casts' target)"
	@echo "  aggconvert 		Convert asciinema casts to GIFs for the documentation. Requires asciinema-agg installed"
	@echo "  help       		Show this help message"

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

# Detect optional flags passed as "targets"
OVERWRITE_FLAG :=
ifneq (,$(filter overwrite,$(MAKECMDGOALS)))
OVERWRITE_FLAG := --overwrite
endif

# Dummy target so make doesn't error on "overwrite"
overwrite:
	@:

AGG_WIDTH     ?= 80
AGG_ROWS     ?= 2
AGG_FONT_SIZE ?= 14
AGG_SPEED     ?= 1.0
ASCIINEMA_DIR := docs/source/_static/asciinema

# Themes
AGG_LIGHT_THEME := github-light
AGG_DARK_THEME  := github-dark

casts:
	@mkdir -p $(ASCIINEMA_DIR)
	@for file in examples/*_demo.py; do \
		base=$$(basename "$$file" .py); \
		echo "Recording non-interactive cast for $$file..."; \
		COLUMNS=$(AGG_WIDTH) LINES=$(AGG_ROWS) asciinema rec $(OVERWRITE_FLAG) \
			--command "uv run python $$file" $(ASCIINEMA_DIR)/$$base.cast; \
	done

casts-interactive:
	@mkdir -p $(ASCIINEMA_DIR)
	@for file in examples/*.py; do \
		case "$$file" in \
			*_interactive.py) \
				base=$$(basename "$$file" .py); \
				echo "Recording interactive cast for $$file..."; \
				COLUMNS=$(AGG_WIDTH) LINES=$(AGG_ROWS) asciinema rec $(OVERWRITE_FLAG) \
					--command "uv run python $$file" $(ASCIINEMA_DIR)/$$base.cast; \
				;; \
		esac; \
	done

casts-clean:
	@echo "Cleaning all asciinema recordings..."
	@rm -rf $(ASCIINEMA_DIR)/*

aggconvert:
	@echo "Converting asciinema casts to animated SVGs (light & dark)..."
	@find $(ASCIINEMA_DIR) -name '*.cast' -print0 | \
	while IFS= read -r -d '' cast; do \
	  base="$${cast%.cast}"; \
	  if [ "$${base##*/}" = "readme_demo" ]; then \
	    echo "  agg $$cast → $${base}.gif"; \
	    agg \
	      --theme $(AGG_DARK_THEME) \
	      --cols $(AGG_WIDTH) \
	      --rows $(AGG_ROWS) \
	      --font-size $(AGG_FONT_SIZE) \
	      --speed $(AGG_SPEED) \
	      "$$cast" "$${base}.gif"; \
	  else \
	    echo "  agg $$cast → $${base}-light.gif"; \
	    agg \
	      --theme $(AGG_LIGHT_THEME) \
	      --cols $(AGG_WIDTH) \
	      --rows $(AGG_ROWS) \
	      --font-size $(AGG_FONT_SIZE) \
	      --speed $(AGG_SPEED) \
	      "$$cast" "$${base}-light.gif"; \
	    echo "  agg $$cast → $${base}-dark.gif"; \
	    agg \
	      --theme $(AGG_DARK_THEME) \
	      --cols $(AGG_WIDTH) \
	      --rows $(AGG_ROWS) \
	      --font-size $(AGG_FONT_SIZE) \
	      --speed $(AGG_SPEED) \
	      "$$cast" "$${base}-dark.gif"; \
	  fi; \
	done

