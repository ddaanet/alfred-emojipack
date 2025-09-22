#!/usr/bin/env bash
set -euo pipefail

# Complete example of setting up and using the Emoji Alfred Generator

echo "=== Emoji Alfred Snippet Generator - Complete Example ==="

# Step 1: Create project directory and files
echo "Creating project structure..."
mkdir -p emoji-alfred-project
cd emoji-alfred-project

# The files would be created here (main script, tests, config files)

# Step 2: Setup with uv
echo "Setting up project with uv..."
if ! command -v uv >/dev/null 2>&1; then
    echo "Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source "$HOME/.cargo/env" || true
fi

# Initialize and install
uv venv
uv pip install click requests

# Step 3: Run tests
echo "Running tests..."
uv run python -m unittest test_emoji_alfred_generator -v

# Step 4: Generate snippet pack with different configurations
echo "Generating emoji snippet packs..."

# Default configuration (semicolon prefix, no suffix)
uv run python emoji_alfred_generator.py \
    --prefix ";" \
    --suffix "" \
    --output "default-emoji.alfredsnippets"

# Slack-style colon prefix and suffix
uv run python emoji_alfred_generator.py \
    --prefix ":" \
    --suffix ":" \
    --output "slack-style-emoji.alfredsnippets"

# GitHub-style semicolon prefix only
uv run python emoji_alfred_generator.py \
    --prefix ";" \
    --suffix "" \
    --output "github-style-emoji.alfredsnippets"

# Test with limited emojis
uv run python emoji_alfred_generator.py \
    --prefix ";" \
    --suffix "" \
    --max-emojis 100 \
    --output "test-emoji.alfredsnippets"

echo "=== Generated Files ==="
ls -la *.alfredsnippets

echo ""
echo "=== Import Instructions ==="
echo "1. Open Alfred Preferences"
echo "2. Go to Features → Snippets"
echo "3. Click the gear icon → Import"
echo "4. Select any of the generated .alfredsnippets files"
echo "5. Enable auto-expansion if desired"
echo ""
echo "=== Usage Examples ==="
echo "After importing, you can use snippets like:"
echo "  ;grinning → 😀 (with default settings)"
echo "  ;+1 → 👍 (with default settings)"
echo "  ;heart → ❤️ (with default settings)"
echo "  :rocket: → 🚀 (with Slack-style prefix/suffix)"
echo "  :thumbsup: → 👍 (with Slack-style prefix/suffix)"

echo ""
echo "✓ Complete setup finished!"