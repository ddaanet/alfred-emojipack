# CLAUDE.md - Project Context

## Project Overview

**Emoji Alfred Snippet Generator** - A Python tool that generates Alfred snippet packs from emoji databases, supporting multiple shortcode formats and comprehensive keyword search.

## Quick Context

- **Language**: Python 3.9+
- **Package Manager**: uv (modern Python package manager)
- **Main Purpose**: Generate `.alfredsnippets` files for Alfred app on macOS
- **Data Source**: [iamcal/emoji-data](https://github.com/iamcal/emoji-data) - 3,000+ emojis
- **Key Features**: Multiple notation styles (`:code:`, custom notation formats), rich keywords, predictable UIDs

## Project Structure

```
emojipack/
├── CLAUDE.md                           # This file - project context
├── README.md                           # Comprehensive user documentation
├── pyproject.toml                      # Project configuration, dependencies
├── uv.lock                            # Locked dependencies
├── justfile                           # Main entry point (task runner)
├── emoji_alfred_generator.py          # Core generator logic
├── test_runner.py                     # Unified test suite
├── Emoji Pack.alfredsnippets          # Generated output (if exists)
├── .python-version                    # Python version specification
├── .gitignore                         # Git ignore patterns
├── .venv/                            # Virtual environment (created by uv)
├── __pycache__/                      # Python cache
├── .pytest_cache/                    # Pytest cache
└── .mypy_cache/                      # MyPy type checker cache
```

## Core Components

### 1. `emoji_alfred_generator.py` (Main Script)
- **Classes**:
  - `EmojiData` (TypedDict): API data structure
  - `AlfredSnippet*` (TypedDict): Alfred snippet structures
  - `EmojiSnippetGenerator`: Main generator class
- **Key Methods**:
  - `fetch_emoji_data()`: Gets data from GitHub API
  - `unicode_to_emoji()`: Converts Unicode codes to emoji
  - `create_snippet()`: Builds individual Alfred snippets
  - `generate_plist()`: Creates info.plist configuration
  - `generate_snippets()`: Main generation orchestrator
- **CLI Interface**: Uses Click for command-line arguments

### 2. `justfile` (Entry Point)
- **Commands**:
  - `setup`: Install uv dependencies, create venv
  - `generate`: Run emoji generator (delegates all options to Python script)
  - `test`: Execute test suite
  - `clean`: Remove generated files and caches
  - `examples`: Show common usage patterns
- **All Generate Options**: Passed directly to Python script without duplication
  - `--prefix`: Snippet prefix (default: `:`)
  - `--suffix`: Snippet suffix (default: `:`)
  - `--output`: Output filename
  - `--max-emojis`: Limit for testing

Example: `just generate --prefix "[" --suffix "]" --output bracket-emoji.alfredsnippets`

### 3. `test_runner.py` (Testing)
- Comprehensive unittest suite
- Tests Unicode conversion, snippet generation, file operations
- Mock API responses for reliable testing
- Validates Alfred snippet format

## Key Data Structures

### Emoji Data (from API)
```python
class EmojiData(TypedDict):
    unified: str        # Unicode code points (e.g., "1F600")
    name: str          # Unicode name (e.g., "GRINNING FACE")
    category: str      # Category (e.g., "Smileys & Emotion")
    subcategory: str   # Subcategory (e.g., "face-smiling")
    short_names: list[str]  # All shortcodes ["grinning", "grinning_face"]
```

### Alfred Snippet Structure
```python
class AlfredSnippetData(TypedDict):
    snippet: str           # The emoji character
    uid: str              # Unique ID: "emojipack-{keyword}-{unicode_name}"
    name: str             # Display name
    keyword: str          # Trigger keyword (without prefix/suffix)
    dontautoexpand: bool  # Alfred auto-expansion setting
```

## Common Patterns

### Notation Format
The generator requires both a prefix and suffix to create complete snippet triggers. Some shortcodes are prefixes of others, so both components are necessary for unambiguous matching.

Examples:
- **Standard colon notation**: `:grinning:` (default, most common)
- **Custom notation**: `[grinning]`, `,grinning.`, `{grinning}`, etc.

### File Generation Process
1. Fetch emoji data from GitHub API
2. Convert Unicode codes to emoji characters
3. Generate multiple snippets per emoji (one per shortcode)
4. Create Alfred-compatible JSON files
5. Package into `.alfredsnippets` ZIP file
6. Generate `info.plist` with prefix/suffix configuration

### Keywords and Search
- Unicode name words: "grinning", "face"
- Category/subcategory: "smileys_emotion", "face_smiling"
- All shortcodes: "grinning", "grinning_face", "+1", "thumbsup"

## Dependencies

### Production
- `click>=8.0`: Command-line interface
- `requests>=2.25`: HTTP requests for emoji data

### Development
- `pytest>=7.0`: Testing framework
- `autopep8`: Code formatting
- `isort`: Import sorting
- `mypy`: Type checking
- `types-requests`: Type stubs

## Common Tasks

### Setup and Run
```bash
just generate           # Default generation (:code:)
just generate --prefix "," --suffix "."  # Custom notation (,code.)
just generate --prefix "[" --suffix "]"  # Custom notation ([code])
just test               # Run tests
```

### Development
```bash
uv run python emoji_alfred_generator.py --help
uv run python test_runner.py
uv run mypy emoji_alfred_generator.py
```

## Configuration

### pyproject.toml Key Sections
- Python 3.9+ requirement
- Click + requests dependencies
- MyPy type checking configuration
- autopep8 code formatting

### Generated Alfred Files
- Individual JSON snippets: `{keyword}-{unicode_name}.json`
- Configuration: `info.plist` with prefix/suffix settings
- Package format: ZIP file with `.alfredsnippets` extension

## External Dependencies

- **Data Source**: GitHub API `https://raw.githubusercontent.com/iamcal/emoji-data/master/emoji.json`
- **Target Platform**: macOS with Alfred Powerpack
- **Output Format**: Alfred Snippets format (ZIP with JSON + plist)

## Recent Context Notes

- Uses modern Python typing with TypedDict
- Comprehensive error handling and logging
- Supports both development and production use cases
- Well-tested with mock API responses
- Clean separation of concerns between data fetching, processing, and file generation
- **Replaced `run.sh` with `justfile`**: Eliminates duplicate option handling by delegating all arguments directly to Python script
- **Modern task runner**: Uses `just` instead of bash script for better maintainability
