set shell := ["bash", "-ceuo", "pipefail"]

# Show available commands
default:
    @just --list

# Install dependencies
setup:
    uv sync --extra dev --quiet

# Generate emoji snippet pack
generate *ARGS:
    uv run python emoji_alfred_generator.py {{ ARGS }}

# Run test suite
test: setup
    uv run python test_runner.py

# Clean generated files and caches
clean:
    rm -f *.alfredsnippets __pycache__ .mypy_cache .venv

# Run type checking
typecheck: setup
    uv run mypy emoji_alfred_generator.py

# Format code
format: setup
    uv run black *.py

# Sort imports
sort-imports: setup
    uv run isort *.py

# Run all code quality checks
lint: typecheck format sort-imports
    @echo "✓ All code quality checks passed!"

# Show usage examples
examples:
    @echo "Examples:"
    @echo "  just generate                                   # Default (:code:)"
    @echo "  just generate --prefix '[' --suffix ']'         # Bracket notation"
    @echo "  just generate --output 'My Emojis.alfredsnippets'"
    @echo "  just generate --max-emojis 50                   # Limited for testing"
