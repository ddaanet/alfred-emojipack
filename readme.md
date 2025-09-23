# Emoji Alfred Snippet Generator

Generate Alfred snippet packs from the iamcal/emoji-data database.

## Quick Start

```sh
# Install dependencies
brew install just uv

# Generate emoji pack
just generate

# Import into Alfred
open "Emoji Pack.alfredsnippets"
```

## Usage

```sh
# Generate with default settings
just generate

# Set custom output filename
just generate --output my-emojis.alfredsnippets

# Set initial prefix and suffix for snippet keywords
just generate --prefix "[" --suffix "]"
```

Alfred snippet packs can be configured to use a common prefix and suffix for all
snippets keywords. The default prefix and suffix in the Emoji Pack are both `:`
(colon notation like `:grinning:`).

The `--prefix` and `--suffix` options set the initial values for the Alfred
snippet keywords. The common prefix and suffix can be configured in the Alfred
snippet pack preferences after importing.

Both a prefix and suffix are required for shortcode disambiguation. Some
shortcodes are prefixes of others (like `grin` and `grinning`), so a suffix
prevents triggering the shorter keyword when typing the longer one.

## Features

- 3,000+ emojis from [emoji-data](https://github.com/iamcal/emoji-data)
- Multiple shortcodes per emoji (GitHub, Slack compatible)
- Rich keywords from Unicode names and categories
- Stable UIDs preserve Alfred's selection intelligence
- Generates `.alfredsnippets` format

Each emoji snippet uses a stable UID format:
`emojipack-{keyword}-{unicode_name}`. The UID is used by Alfred to remember
which item was selected when multiple results match your query. Using stable
UIDs ensures you don't lose Alfred's selection intelligence when regenerating
the snippet pack.

## Requirements

- Python 3.12+
- macOS with Alfred Powerpack
- [uv](https://github.com/astral-sh/uv), fast python package manager
- [just](https://github.com/casey/just), convenient task runner

## License

MIT License
