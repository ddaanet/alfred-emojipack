# Emoji Alfred Snippet Generator

Generate Alfred snippet packs from freely available emoji databases with multiple shortcodes and comprehensive keyword support. Requires both prefix and suffix for proper shortcode disambiguation.

## Features

- **Comprehensive Emoji Database**: Uses `iamcal/emoji-data` with 3,000+ emojis
- **Multiple Shortcodes**: Creates separate snippets for each emoji shortcode
  (GitHub, Slack compatible)
- **Custom Notation Formats**: Supports any prefix+suffix combination (both
  required)
- **Rich Keywords**: Includes official Unicode names, categories, and
  shortcodes
- **Predictable UIDs**: Uses format `emojipack-{keyword}-{unicode_name}` with
  spaces replaced by underscores
- **Customizable Prefix/Suffix**: Configure snippet triggers via info.plist
  (default: `:` prefix and suffix, supports custom notation)
- **Alfred Format**: Generates proper `.alfredsnippets` files for direct import

## Requirements

- Python 3.8+
- [uv](https://github.com/astral-sh/uv) package manager
- macOS with Alfred Powerpack
- [just](https://github.com/casey/just) task runner

### Installing Dependencies

If you don't have the required tools installed:

- `just` is a handy task runner
- `uv` is a fast python package manager

```sh
brew install just uv
```

## Quick Start

```sh
# Generate emoji snippet pack
just generate

# Import emoji snippet pack into Alfred
open "Emoji Pack.alfredsnippets"
```

## Usage

### Basic Generation

```sh
just generate
```

Creates `Emoji Pack.alfredsnippets` with default `:` prefix and suffix.

### Custom Configuration

Both a prefix and a suffix are needed to create unambiguous snippet triggers.
Some shortcodes are prefixes of others (like `grin` and `grinning`), so a
suffix is needed to avoid triggering the shorter keyword when intending to use
the longer one.

You can configure the affix in Alfred Preferences. But you can also set it
when generating the snippet pack using the `--prefix` and `--suffix` options.

```sh
# Use bracket notation
just generate --prefix "[" --suffix "]" --output bracket-emoji.alfredsnippets

# Use custom notation
just generate --prefix "," --suffix "." --output custom-emoji.alfredsnippets

# Limit emojis for testing
just generate --max-emojis 100 --output test-emoji.alfredsnippets
```

### Other Commands

```sh
# Show available commands
just

# Get help for generate command options
just generate --help
```

## Notation Format

### Standard Colon Notation `:code:`

The most common emoji notation style:

```sh
just generate  # Uses default : prefix and : suffix
```

| Trigger      | Emoji | Name           |
| ------------ | ----- | -------------- |
| `:grinning:` | 😀    | Grinning Face  |
| `:+1:`       | 👍    | Thumbs Up Sign |
| `:heart:`    | ❤️    | Red Heart      |

### Custom Notation Examples

Bracket notation:

```sh
just generate --prefix "[" --suffix "]"
```

| Trigger      | Emoji | Name           |
| ------------ | ----- | -------------- |
| `[grinning]` | 😀    | Grinning Face  |
| `[+1]`       | 👍    | Thumbs Up Sign |
| `[heart]`    | ❤️    | Red Heart      |

Comma-period notation:

```sh
just generate --prefix "," --suffix "."
```

| Trigger      | Emoji | Name           |
| ------------ | ----- | -------------- |
| `,grinning.` | 😀    | Grinning Face  |
| `,+1.`       | 👍    | Thumbs Up Sign |
| `,heart.`    | ❤️    | Red Heart      |

## Data Source

Uses the excellent [emoji-data](https://github.com/iamcal/emoji-data) project by Cal Henderson, which provides:

- Complete Unicode emoji coverage
- Multiple platform shortcodes (GitHub, Slack, etc.)
- Comprehensive metadata and categorization
- Regular updates with new Unicode releases

## Generated File Structure

Each `.alfredsnippets` file contains:

- Individual JSON snippet files named `{keyword}-{unicode_name}.json` (e.g., `grinning-GRINNING_FACE.json`)
- `info.plist` with prefix/suffix configuration
- UIDs with format `emojipack-{keyword}-{unicode_name}`
- Clean keywords without embedded prefixes

## License

MIT License - see project files for details.

## Credits

- [emoji-data](https://github.com/iamcal/emoji-data) by Cal Henderson
- [Alfred](https://www.alfredapp.com/) by Running with Crayons
- Emoji artwork by respective platform vendors
