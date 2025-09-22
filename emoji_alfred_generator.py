#!/usr/bin/env python3
"""
Emoji Alfred Snippet Pack Generator

Generates Alfred snippet packs from freely available emoji databases.
Creates multiple shortcuts for emojis with multiple shortcodes.
"""

import json
import tempfile
import zipfile
from pathlib import Path
from uuid import uuid4
import click
import requests
from typing import Dict, List, Set, Any


class EmojiSnippetGenerator:
    def __init__(self, prefix: str = ";", suffix: str = ""):
        self.prefix = prefix
        self.suffix = suffix
        self.emoji_data = []

    def fetch_emoji_data(self) -> List[Dict[str, Any]]:
        """Fetch emoji data from iamcal/emoji-data repository."""
        url = "https://raw.githubusercontent.com/iamcal/emoji-data/master/emoji.json"
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.json()

    def generate_keywords(self, emoji: Dict[str, Any]) -> Set[str]:
        """Generate keywords for an emoji based on name, category, and shortcodes."""
        keywords = set()

        # Add official name words (lowercased, no punctuation)
        name_words = emoji.get("name", "").lower().replace("_", " ").split()
        keywords.update(word.strip(".,!?:;") for word in name_words if word.strip(".,!?:;"))

        # Add category and subcategory
        category = emoji.get("category", "")
        if category:
            keywords.add(category.lower().replace(" ", "_"))

        subcategory = emoji.get("subcategory", "")
        if subcategory:
            keywords.add(subcategory.lower().replace(" ", "_"))

        # Add all shortcodes as keywords
        short_names = emoji.get("short_names", [])
        keywords.update(short_names)

        return keywords

    def create_snippet(self, emoji_char: str, keyword: str, name: str) -> Dict[str, Any]:
        """Create a single Alfred snippet structure."""
        return {
            "alfredsnippet": {
                "snippet": emoji_char,
                "uid": str(uuid4()).upper(),
                "name": name,
                "keyword": keyword,  # No prefix/suffix - handled by info.plist
                "dontautoexpand": False
            }
        }

    def unicode_to_emoji(self, unified: str) -> str:
        """Convert unified Unicode codepoint to emoji character."""
        if not unified:
            return ""

        # Handle multiple codepoints separated by hyphens
        codepoints = unified.split("-")
        chars = []

        for cp in codepoints:
            try:
                chars.append(chr(int(cp, 16)))
            except (ValueError, OverflowError):
                return ""

        return "".join(chars)

    def generate_snippets(self) -> List[Dict[str, Any]]:
        """Generate all emoji snippets."""
        self.emoji_data = self.fetch_emoji_data()
        snippets = []

        for emoji in self.emoji_data:
            unified = emoji.get("unified", "")
            if not unified:
                continue

            emoji_char = self.unicode_to_emoji(unified)
            if not emoji_char:
                continue

            # Generate keywords for this emoji
            keywords = self.generate_keywords(emoji)

            # Get shortcodes
            short_names = emoji.get("short_names", [])
            if not short_names:
                continue

            # Create a snippet for each shortcode
            for short_name in short_names:
                name = emoji.get("name", short_name).title()
                snippet = self.create_snippet(
                    emoji_char=emoji_char,
                    keyword=short_name,
                    name=f"{emoji_char} {name}"
                )
                snippets.append(snippet)

        return snippets

    def create_info_plist(self) -> str:
        """Create info.plist content with prefix and suffix settings."""
        plist_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
\t<key>snippetkeywordprefix</key>
\t<string>{self.prefix}</string>
\t<key>snippetkeywordsuffix</key>
\t<string>{self.suffix}</string>
</dict>
</plist>'''
        return plist_content

    def create_alfred_snippet_pack(self, snippets: List[Dict[str, Any]],
                                 output_path: Path) -> None:
        """Create the .alfredsnippets file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create individual JSON files for each snippet
            json_files = []
            for snippet in snippets:
                uid = snippet["alfredsnippet"]["uid"]
                name = snippet["alfredsnippet"]["name"]
                # Clean filename
                clean_name = "".join(c for c in name if c.isalnum() or c in " -_")[:50]
                filename = f"{clean_name} [{uid}].json"

                file_path = temp_path / filename
                with file_path.open("w", encoding="utf-8") as f:
                    json.dump(snippet, f, ensure_ascii=False, indent=2)

                json_files.append(filename)

            # Create info.plist file
            info_plist_content = self.create_info_plist()
            info_plist_path = temp_path / "info.plist"
            with info_plist_path.open("w", encoding="utf-8") as f:
                f.write(info_plist_content)

            # Create ZIP file
            with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
                # Add all JSON snippet files
                for json_file in json_files:
                    file_path = temp_path / json_file
                    zf.write(file_path, json_file)

                # Add info.plist
                zf.write(info_plist_path, "info.plist")


@click.command()
@click.option("--prefix", "-p", default=";",
              help="Prefix for snippet keywords (default: ';')")
@click.option("--suffix", "-s", default="",
              help="Suffix for snippet keywords (default: '')")
@click.option("--output", "-o", type=click.Path(),
              default="emoji-snippets.alfredsnippets",
              help="Output filename (default: emoji-snippets.alfredsnippets)")
@click.option("--max-emojis", "-m", type=int,
              help="Maximum number of emojis to process (for testing)")
def main(prefix: str, suffix: str, output: str, max_emojis: int) -> None:
    """Generate Alfred emoji snippet pack from emoji database."""
    set_euo_pipefail()

    click.echo("Fetching emoji data...")
    generator = EmojiSnippetGenerator(prefix=prefix, suffix=suffix)

    click.echo("Generating snippets...")
    snippets = generator.generate_snippets()

    if max_emojis:
        snippets = snippets[:max_emojis]

    click.echo(f"Generated {len(snippets)} emoji snippets")

    output_path = Path(output)
    click.echo(f"Creating Alfred snippet pack: {output_path}")
    generator.create_alfred_snippet_pack(snippets, output_path)

    click.echo(f"✓ Created {output_path} with {len(snippets)} emoji snippets")
    click.echo("Import this file into Alfred via Preferences > Features > Snippets")


def set_euo_pipefail():
    """Set equivalent of shell 'set -euo pipefail' for error handling."""
    import sys
    import signal

    # Exit on any exception
    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        click.echo(f"Error: {exc_value}", err=True)
        sys.exit(1)

    sys.excepthook = handle_exception

    # Handle SIGPIPE
    signal.signal(signal.SIGPIPE, signal.SIG_DFL)


if __name__ == "__main__":
    main()