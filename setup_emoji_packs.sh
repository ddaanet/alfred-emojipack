#!/bin/bash
set -euo pipefail

# Alfred Emoji Pack Setup Script
# Creates emoji snippet packs for Alfred using Emojibase data

readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly GENERATOR_SCRIPT="${SCRIPT_DIR}/alfred_emoji_generator.py"

# Install dependencies if needed
install_deps() {
    echo "Installing Python dependencies..."
    pip install requests click
}

# Generate different emoji packs
generate_packs() {
    local output_dir="${1:-./alfred-emoji-packs}"

    echo "Creating output directory: ${output_dir}"
    mkdir -p "${output_dir}"

    echo "Generating emoji packs..."

    # GitHub-style shortcodes (most common)
    python3 "${GENERATOR_SCRIPT}" \
        --shortcodes github \
        --output "${output_dir}/emoji-github.alfredsnippets" \
        --bundle-name "Emoji (GitHub Style)"

    # Slack/CLDR style shortcodes
    python3 "${GENERATOR_SCRIPT}" \
        --shortcodes cldr \
        --output "${output_dir}/emoji-slack.alfredsnippets" \
        --bundle-name "Emoji (Slack/CLDR Style)"

    # Limited pack (first 100 emojis for testing)
    python3 "${GENERATOR_SCRIPT}" \
        --shortcodes github \
        --max-emojis 100 \
        --output "${output_dir}/emoji-sample.alfredsnippets" \
        --bundle-name "Emoji Sample Pack"

    echo "Generated packs in: ${output_dir}"
    echo "Import .alfredsnippets files into Alfred via:"
    echo "Alfred Preferences > Features > Snippets > Import"
}

# Show usage
usage() {
    cat << EOF
Usage: $0 [COMMAND] [OPTIONS]

Commands:
    install     Install Python dependencies
    generate    Generate Alfred emoji snippet packs

Options:
    -o DIR      Output directory (default: ./alfred-emoji-packs)
    -h          Show this help

Examples:
    $0 install
    $0 generate
    $0 generate -o ~/Downloads/emoji-packs
EOF
}

# Main execution
main() {
    case "${1:-}" in
        install)
            install_deps
            ;;
        generate)
            shift
            local output_dir="./alfred-emoji-packs"

            while getopts "o:h" opt; do
                case $opt in
                    o) output_dir="$OPTARG" ;;
                    h) usage; exit 0 ;;
                    *) usage; exit 1 ;;
                esac
            done

            generate_packs "$output_dir"
            ;;
        -h|--help|help)
            usage
            exit 0
            ;;
        *)
            echo "Error: Unknown command '${1:-}'"
            usage
            exit 1
            ;;
    esac
}

main "$@"
