#!/usr/bin/env bash
set -euo pipefail

# Emoji Alfred Generator Setup and Run Script

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

usage() {
    cat << EOF
Usage: $0 [COMMAND] [OPTIONS]

Commands:
    setup       Install dependencies and setup environment
    generate    Generate emoji snippet pack
    test        Run test suite
    clean       Clean up generated files
    help        Show this help

Generate Options:
    -p, --prefix PREFIX     Snippet keyword prefix (default: ';')
    -o, --output FILE       Output filename (default: emoji-snippets.alfredsnippets)
    -m, --max-emojis N      Limit number of emojis for testing

Examples:
    $0 setup
    $0 generate
    $0 generate -p ":" -o custom-emoji.alfredsnippets
    $0 test
EOF
}

setup() {
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
}

generate() {
    local prefix=";"
    local output="emoji-snippets.alfredsnippets"
    local max_emojis=""

    # Parse options
    while [[ $# -gt 0 ]]; do
        case $1 in
            -p|--prefix)
                prefix="$2"
                shift 2
                ;;
            -o|--output)
                output="$2"
                shift 2
                ;;
            -m|--max-emojis)
                max_emojis="$2"
                shift 2
                ;;
            *)
                echo "Unknown option: $1" >&2
                usage
                exit 1
                ;;
        esac
    done

    echo "Generating emoji snippet pack..."

    local cmd=(uv run python emoji_alfred_generator.py --prefix "$prefix" --output "$output")
    if [[ -n "$max_emojis" ]]; then
        cmd+=(--max-emojis "$max_emojis")
    fi

    "${cmd[@]}"

    echo "✓ Generated $output"
}

run_tests() {
    echo "Running test suite..."
    uv run python -m unittest test_emoji_alfred_generator -v
    echo "✓ All tests passed!"
}

clean() {
    echo "Cleaning up generated files..."

    find . -name "*.alfredsnippets" -delete 2>/dev/null || true
    find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    find . -name "*.pyc" -delete 2>/dev/null || true

    if [[ -d ".venv" ]]; then
        rm -rf .venv
        echo "Removed virtual environment"
    fi

    echo "✓ Cleanup complete!"
}

main() {
    case "${1:-help}" in
        setup)
            shift
            setup "$@"
            ;;
        generate)
            shift
            generate "$@"
            ;;
        test)
            shift
            run_tests "$@"
            ;;
        clean)
            shift
            clean "$@"
            ;;
        help|--help|-h)
            usage
            ;;
        *)
            echo "Unknown command: $1" >&2
            usage
            exit 1
            ;;
    esac
}

# Only run main if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
