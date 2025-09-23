set shell := ["bash", "-ceuo", "pipefail"]

default:
    @just --list

generate *ARGS:
    uv run python emoji_alfred_generator.py {{ ARGS }}

test:
    uv run --group dev python test_runner.py

clean:
    rm -rf *.alfredsnippets __pycache__ .mypy_cache .venv

typecheck:
    uv run --group dev mypy emoji_alfred_generator.py

format:
    uv run --group dev autopep8 --in-place *.py
    uv run --group dev isort *.py

lint: typecheck format
