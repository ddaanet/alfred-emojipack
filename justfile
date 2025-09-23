set shell := ["bash", "-ceuo", "pipefail"]

default:
    @just --list

setup:
    @uv sync --extra dev --quiet

generate *ARGS:
    uv run python emoji_alfred_generator.py {{ ARGS }}

test: setup
    uv run python test_runner.py

clean:
    rm -f *.alfredsnippets __pycache__ .mypy_cache .venv

typecheck: setup
    uv run mypy emoji_alfred_generator.py

format: setup
    uv run autopep8 --in-place *.py && uv run isort *.py

lint: typecheck format
    @echo "✓ Done"
