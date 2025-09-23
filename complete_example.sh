#!/usr/bin/env bash
set -euo pipefail

# Complete example of setting up and using the Emoji Alfred Generator

echo "=== Emoji Alfred Snippet Generator - Complete Example ==="

# Step 1: Navigate to project directory
echo "Navigating to project directory..."
cd ~/code/emojipack

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
uv run python test_runner.py

# Step 4: Generate snippet pack with different configurations
echo "Generating emoji snippet packs..."

# Default configuration (colon prefix and suffix)
uv run python emoji_alfred_generator.py \
    --output "default-emoji.alfredsnippets"

# Bracket notation
uv run python emoji_alfred_generator.py \
    --prefix "[" --suffix "]" --output "bracket-emoji.alfredsnippets"

# Custom notation
uv run python emoji_alfred_generator.py \
    --prefix "," --suffix "." --output "comma-dot-emoji.alfredsnippets"

# Test with limited emojis
uv run python emoji_alfred_generator.py \
    --max-emojis 100 --output "test-emoji.alfredsnippets"

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
echo "  :grinning: → 😀 (with default settings)"
echo "  :+1: → 👍 (with default settings)"
echo "  :heart: → ❤️ (with default settings)"
echo "  [rocket] → 🚀 (with bracket notation)"
echo "  [thumbsup] → 👍 (with bracket notation)"
echo "  ,grinning. → 😀 (with comma-dot notation)"
echo "  ,+1. → 👍 (with comma-dot notation)"
echo "  ,heart. → ❤️ (with custom notation)"

echo ""
echo "✓ Complete setup finished!"
echo ""
echo "=== Generated File Structure ==="
echo "Each .alfredsnippets file contains:"
echo "  - Individual JSON files named {keyword}-{unicode_name}.json (e.g., grinning-GRINNING_FACE.json)"
echo "  - info.plist with prefix/suffix configuration"
echo "  - UIDs with format emojipack-{keyword}-{unicode_name}"
