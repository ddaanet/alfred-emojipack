# Emoji Alfred Snippet Generator

Generate Alfred snippet packs from freely available emoji databases with multiple shortcodes and comprehensive keyword support.

## Features

- **Comprehensive Emoji Database**: Uses `iamcal/emoji-data` with 3,000+ emojis
- **Multiple Shortcodes**: Creates separate snippets for each emoji shortcode (GitHub, Slack compatible)
- **Rich Keywords**: Includes official Unicode names, categories, and all known shortcodes
- **Predictable UIDs**: Uses Unicode names as unique identifiers with `emojipack:` prefix
- **Customizable Prefix/Suffix**: Configure snippet triggers via info.plist (default: `;` prefix)
- **Alfred Format**: Generates proper `.alfredsnippets` files for direct import

## Requirements

- Python 3.8+
- [uv](https://github.com/astral-sh/uv) package manager
- macOS with Alfred Powerpack

## Quick Start

```bash
# Navigate to the project directory
cd ~/code/emojipack

# Make the script executable
chmod +x run.sh

# Setup environment and dependencies
./run.sh setup

# Generate emoji snippet pack
./run.sh generate

# Import emoji-snippets.alfredsnippets into Alfred
```

## Usage

### Basic Generation

```bash
./run.sh generate
```

Creates `emoji-snippets.alfredsnippets` with default `;` prefix.

### Custom Configuration

```bash
# Use colon prefix and suffix like Slack
./run.sh generate -p ":" -s ":" -o slack-emoji.alfredsnippets

# Use semicolon prefix only (default)
./run.sh generate -p ";" -s "" -o github-emoji.alfredsnippets

# Limit emojis for testing
./run.sh generate -m 100 -o test-emoji.alfredsnippets
```

### Testing

```bash
# Run complete test suite (functionality + unit tests)
./run.sh test

# Or run directly
python test_runner.py
```

### Cleanup

```bash
./run.sh clean
```

## Alfred Integration

1. Generate the snippet pack: `./run.sh generate`
2. Open Alfred Preferences → Features → Snippets
3. Click the gear icon → Import
4. Select the generated `.alfredsnippets` file
5. Enable auto-expansion if desired

## Example Snippets

With default `;` prefix:

| Trigger | Emoji | Name |
|---------|-------|------|
| `;grinning` | 😀 | Grinning Face |
| `;+1` | 👍 | Thumbs Up Sign |
| `;thumbsup` | 👍 | Thumbs Up Sign |
| `;heart` | ❤️ | Red Heart |

With Slack-style `:` prefix and suffix:

| Trigger | Emoji | Name |
|---------|-------|------|
| `:grinning:` | 😀 | Grinning Face |
| `:+1:` | 👍 | Thumbs Up Sign |
| `:heart:` | ❤️ | Red Heart |

## Keywords and Search

Each emoji includes keywords from:
- **Official Unicode name**: "grinning", "face", "thumbs", "up"
- **Categories**: "smileys_emotion", "people_body"
- **All shortcodes**: "grinning", "grinning_face", "+1", "thumbsup"

## Data Source

Uses the excellent [emoji-data](https://github.com/iamcal/emoji-data) project by Cal Henderson, which provides:
- Complete Unicode emoji coverage
- Multiple platform shortcodes (GitHub, Slack, etc.)
- Comprehensive metadata and categorization
- Regular updates with new Unicode releases

## Project Structure

```
~/code/emojipack/
├── emoji_alfred_generator.py    # Main generator script
├── test_runner.py              # Unified test suite
├── run.sh                      # Setup and run script
├── pyproject.toml             # Project configuration
└── README.md                  # Documentation
```

## Generated File Structure

Each `.alfredsnippets` file contains:
- Individual JSON snippet files with UIDs like `emojipack:GRINNING FACE`
- `info.plist` with prefix/suffix configuration
- Clean keywords without embedded prefixes

## Development

```bash
# Setup development environment
./run.sh setup

# Run tests
./run.sh test

# Generate with debug limiting
./run.sh generate -m 50

# Generate with custom prefix/suffix
./run.sh generate -p ":" -s ":" -m 50

# Manual execution
uv run python emoji_alfred_generator.py --help
```

## License

MIT License - see project files for details.

## Credits

- [emoji-data](https://github.com/iamcal/emoji-data) by Cal Henderson
- [Alfred](https://www.alfredapp.com/) by Running with Crayons
- Emoji artwork by respective platform vendors
