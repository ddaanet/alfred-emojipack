set shell := ["bash", "-ceuo", "pipefail"]

default:
    @just --list

generate *ARGS:
    uv sync --inexact --quiet
    uv run python emoji_alfred_generator.py {{ ARGS }}

_setup:
    uv sync --extra dev --quiet

test: _setup
    uv run python test_runner.py

clean:
    rm -rf *.alfredsnippets __pycache__ .mypy_cache .venv

typecheck: _setup
    uv run mypy emoji_alfred_generator.py

format: _setup
    uv run autopep8 --in-place *.py && uv run isort *.py

lint: typecheck format
    @echo "✓ Done"
