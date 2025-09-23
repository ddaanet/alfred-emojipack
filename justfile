set shell := ["bash", "-ceuo", "pipefail"]

default:
    @just --list

generate *ARGS:
    uv run python emoji_alfred_generator.py {{ ARGS }}

test:
    uv run --extra dev test_runner.py

clean:
    rm -rf *.alfredsnippets __pycache__ .mypy_cache .venv

typecheck:
    uv run --extra dev mypy emoji_alfred_generator.py

format:
    uv run --extra dev autopep8 --in-place *.py && uv run isort *.py

lint: typecheck format
    @echo "✓ Done"
