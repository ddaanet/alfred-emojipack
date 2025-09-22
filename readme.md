# Alfred Emoji Snippet Pack Generator

Generate comprehensive emoji snippet packs for Alfred using the **Emojibase** database - the most up-to-date and feature-rich emoji database available.

## Features

✅ **Official Unicode names**  
✅ **Multiple shortcode sets** (GitHub, Slack/CLDR, emojibase)  
✅ **Rich keywords and tags** for searchability  
✅ **Up-to-date emoji data** (Emoji 16.0 support)  
✅ **Configurable output** (locale, shortcode style, size limits)  

## Quick Start

```bash
# Install dependencies
./setup_emoji_packs.sh install

# Generate emoji packs
./setup_emoji_packs.sh generate

# Import .alfredsnippets files into Alfred:
# Alfred Preferences > Features > Snippets > Import
```

## Data Sources

### Primary: Emojibase (Recommended)
- **Repository**: https://github.com/milesj/emojibase
- **Features**: Complete Unicode data, multiple shortcode sets, keywords
- **CDN Access**: `https://cdn.jsdelivr.net/npm/emojibase-data@latest/`

### Alternative Options:
- **emoji-data** (iamcal): GitHub/Slack style shortcodes
- **emojilib** (muan): Rich keyword database  
- **unicode-emoji-json** (muan): Official Unicode data

## Usage Examples

```bash
# Generate with specific options
python3 alfred_emoji_generator.py \
  --locale en \
  --shortcodes github \
  --max-emojis 500 \
  --output custom-emoji.alfredsnippets

# Different shortcode styles
python3 alfred_emoji_generator.py --shortcodes cldr    # Slack/CLDR style
python3 alfred_emoji_generator.py --shortcodes github  # GitHub style
```

## Output Format

Generated Alfred snippets include:
- **Snippet**: The actual emoji character 
- **Keyword**: Primary shortcode + additional keywords
- **Name**: Official Unicode annotation
- **UID**: Unique identifier for Alfred

Example snippet in Alfred:
- **Keyword**: `grinning face smile happy`
- **Snippet**: `😀`
- **Name**: `grinning face`

## Testing

```bash
# Run all tests
./test_runner.sh

# Run specific test suites
./test_runner.sh python
./test_runner.sh shell
./test_runner.sh perf
```

## File Structure

```
alfred-emoji-generator/
├── alfred_emoji_generator.py    # Main generator script
├── setup_emoji_packs.sh        # Setup and generation script
├── test_runner.sh               # Test suite
└── README.md                    # This file
```

## Alfred Integration

1. Run the generator to create `.alfredsnippets` files
2. Open Alfred Preferences
3. Go to Features > Snippets
4. Click the '+' button and select "Import"
5. Choose your generated `.alfredsnippets` file

Now you can type emoji shortcodes in any app and Alfred will expand them to emoji characters!
