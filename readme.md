# Emoji Alfred Snippet Generator

Generate Alfred snippet packs from freely available emoji databases with multiple shortcodes and comprehensive keyword support. Requires both prefix and suffix for proper shortcode disambiguation.

## Features

- **Comprehensive Emoji Database**: Uses `iamcal/emoji-data` with 3,000+ emojis
- **Multiple Shortcodes**: Creates separate snippets for each emoji shortcode (GitHub, Slack compatible)
- **Custom Notation Formats**: Supports any prefix+suffix combination (both required)
- **Rich Keywords**: Includes official Unicode names, categories, and all known shortcodes
- **Predictable UIDs**: Uses format `emojipack-{keyword}-{unicode_name}` with spaces replaced by underscores
- **Customizable Prefix/Suffix**: Configure snippet triggers via info.plist (default: `:` prefix and suffix, supports custom notation)
- **Alfred Format**: Generates proper `.alfredsnippets` files for direct import

## Requirements

- Python 3.8+
- [uv](https://github.com/astral-sh/uv) package manager
- macOS with Alfred Powerpack

### Installing uv

If you don't have uv installed:

```bash
brew install uv
```

## Quick Start

```bash
# Setup environment and dependencies
./run.sh setup

# Generate emoji snippet pack
./run.sh generate

# Import emoji snippet pack into Alfred
open "Emoji Pack.alfredsnippets"
```

## Usage

### Basic Generation

```bash
./run.sh generate
```

Creates `Emoji Pack.alfredsnippets` with default `:` prefix and suffix.

### Custom Configuration

```bash
# Use bracket notation
./run.sh generate -p "[" -s "]" -o bracket-emoji.alfredsnippets

# Use colon prefix and suffix (default)
./run.sh generate -p ":" -s ":" -o colon-emoji.alfredsnippets

# Use custom notation
./run.sh generate -p "," -s "." -o custom-emoji.alfredsnippets

# Limit emojis for testing
./run.sh generate -m 100 -o test-emoji.alfredsnippets
```

### Testing

```bash
# Run complete test suite (functionality + unit tests)
./run.sh test

# Or run directly with uv
uv run python test_runner.py
```

### Cleanup

```bash
./run.sh clean
```

## Alfred Integration

Double click on the generated file, or doing it at the command line:

```bash
open "Emoji Pack.alfredsnippets"
```

## Notation Format

The both a prefix and suffix are needed to create unambiguous snippet triggers.
Some shortcodes are prefixes of others (like `grin` and `grinning`), so a
suffix is needed to avoid triggering the shorter keyword when intending to use
the longer one.

### Standard Colon Notation `:code:`

The most common emoji notation style:

```bash
./run.sh generate  # Uses default : prefix and : suffix
```

| Trigger      | Emoji | Name           |
| ------------ | ----- | -------------- |
| `:grinning:` | 😀    | Grinning Face  |
| `:+1:`       | 👍    | Thumbs Up Sign |
| `:heart:`    | ❤️    | Red Heart      |

### Custom Notation Examples

Bracket notation:

```bash
./run.sh generate -p "[" -s "]"
```

| Trigger      | Emoji | Name           |
| ------------ | ----- | -------------- |
| `[grinning]` | 😀    | Grinning Face  |
| `[+1]`       | 👍    | Thumbs Up Sign |
| `[heart]`    | ❤️    | Red Heart      |

Comma-period notation:

```bash
./run.sh generate -p "," -s "."
```

| Trigger      | Emoji | Name           |
| ------------ | ----- | -------------- |
| `,grinning.` | 😀    | Grinning Face  |
| `,+1.`       | 👍    | Thumbs Up Sign |
| `,heart.`    | ❤️    | Red Heart      |

Custom combinations:

```bash
./run.sh generate -p "~" -s "~"  # ~code~
./run.sh generate -p "{" -s "}"  # {code}
```

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

- Individual JSON snippet files named `{keyword}-{unicode_name}.json` (e.g., `grinning-GRINNING_FACE.json`)
- `info.plist` with prefix/suffix configuration
- UIDs with format `emojipack-{keyword}-{unicode_name}`
- Clean keywords without embedded prefixes

## Development

```bash
# Setup development environment
./run.sh setup

# Run tests
./run.sh test

# Generate with debug limiting
./run.sh generate -m 50

# Generate with custom notation
./run.sh generate -p "," -s "." -m 50

# Manual execution with uv
uv run python emoji_alfred_generator.py --help

# Direct generation with uv
uv run python emoji_alfred_generator.py --output "my-emoji.alfredsnippets"
uv run python emoji_alfred_generator.py --prefix "[" --suffix "]" --output "bracket-emoji.alfredsnippets"
```

## License

MIT License - see project files for details.

## Credits

- [emoji-data](https://github.com/iamcal/emoji-data) by Cal Henderson
- [Alfred](https://www.alfredapp.com/) by Running with Crayons
- Emoji artwork by respective platform vendors
