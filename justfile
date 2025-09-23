set shell := ["bash", "-ceuo", "pipefail"]

# Show available commands
default:
    @just --list

# Install dependencies and setup environment
setup:
    echo "Setting up emoji Alfred generator..."

    # Check if uv is installed
    if ! command -v uv >/dev/null 2>&1; then
        echo "Error: uv is not installed. Please install uv first:"
        echo "curl -LsSf https://astral.sh/uv/install.sh | sh"
        exit 1
    fi

    echo "Creating virtual environment with uv..."
    uv venv

    echo "Installing dependencies..."
    uv pip install -e ".[dev]"

    echo "✓ Setup complete!"
    echo "Virtual environment created in .venv/"

# Generate emoji snippet pack (delegates all options to Python script)
generate *ARGS:
    #!/usr/bin/env bash
    set -euo pipefail
    echo "Generating emoji snippet pack..."
    uv run python emoji_alfred_generator.py {{ ARGS }}
    echo "✓ Generation complete!"

# Run test suite
test:
    #!/usr/bin/env bash
    set -euo pipefail
    echo "Running test suite..."
    uv run python test_runner.py

# Clean up generated files and caches
clean:
    #!/usr/bin/env bash
    set -euo pipefail
    echo "Cleaning up generated files..."

    find . -name "*.alfredsnippets" -delete 2>/dev/null || true
    find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    find . -name "*.pyc" -delete 2>/dev/null || true
    find . -name ".pytest_cache" -type d -exec rm -rf {} + 2>/dev/null || true
    find . -name ".mypy_cache" -type d -exec rm -rf {} + 2>/dev/null || true

    if [[ -d ".venv" ]]; then
        rm -rf .venv
        echo "Removed virtual environment"
    fi

    echo "✓ Cleanup complete!"

# Development commands

# Run type checking with mypy
typecheck:
    uv run mypy emoji_alfred_generator.py

# Format code with black
format:
    uv run black emoji_alfred_generator.py test_runner.py

# Sort imports with isort
sort-imports:
    uv run isort emoji_alfred_generator.py test_runner.py

# Run all code quality checks
lint: typecheck format sort-imports
    @echo "✓ All code quality checks passed!"

# Quick examples for common usage patterns
examples:
    @echo "Common usage examples:"
    @echo ""
    @echo "Default colon notation (:code:):"
    @echo "  just generate"
    @echo ""
    @echo "Custom bracket notation ([code]):"
    @echo "  just generate --prefix '[' --suffix ']'"
    @echo ""
    @echo "Custom output file:"
    @echo "  just generate --output 'My Emojis.alfredsnippets'"
    @echo ""
    @echo "Limit emojis for testing:"
    @echo "  just generate --max-emojis 50"
    @echo ""
    @echo "Combine options:"
    @echo "  just generate -p ',' -s '.' -o comma-emojis.alfredsnippets -m 100"
