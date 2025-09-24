default:
    @just --list

generate *ARGS:
    uv run python emojipack_generator.py {{ ARGS }}

alfred: generate
    open "Emoji Pack.alfredsnippets"

test:
    uv run --group dev python test_runner.py

clean:
    rm -rf *.alfredsnippets __pycache__ .mypy_cache .venv

typecheck:
    uv run --group dev mypy *.py

format:
    uv run --group dev autopep8 --in-place *.py
    uv run --group dev isort *.py

lint: typecheck format
