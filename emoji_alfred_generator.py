#!/usr/bin/env python3
"""
Emoji Alfred Snippet Pack Generator

Generates Alfred snippet packs from freely available emoji databases.
Creates multiple shortcuts for emojis with multiple shortcodes.
"""

import json
import sys
import textwrap
import zipfile
from pathlib import Path
from typing import TypedDict, cast
from xml.sax.saxutils import escape

import click
import requests


class EmojiData(TypedDict):
    """Structure for emoji data from the API.

    Based on analysis, all these fields are always present and never empty
    in the iamcal/emoji-data dataset.
    """
    unified: str
    name: str
    category: str
    subcategory: str
    short_names: list[str]


class AlfredSnippetData(TypedDict):
    """Structure for Alfred snippet metadata."""
    snippet: str
    uid: str
    name: str
    keyword: str
    dontautoexpand: bool


class AlfredSnippet(TypedDict):
    """Complete snippet structure with Alfred metadata."""
    alfredsnippet: AlfredSnippetData


class AlfredSnippetWithName(AlfredSnippet, total=False):
    """Snippet data with temporary metadata for processing."""
    _unicode_name: str


class EmojiSnippetGenerator:
    def __init__(self, prefix: str = ";", suffix: str = ""):
        self.prefix: str = prefix
        self.suffix: str = suffix
        self.emoji_data: list[EmojiData] = []

    def fetch_emoji_data(self) -> list[EmojiData]:
        """Fetch emoji data from iamcal/emoji-data repository."""
        url = "https://raw.githubusercontent.com/iamcal/emoji-data/master/emoji.json"
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return cast(list[EmojiData], response.json())

    def generate_keywords(self, emoji: EmojiData) -> list[str]:
        """Generate keywords for an emoji based on name and category."""
        all_keywords = emoji["subcategory"].split("-")
        name_words = set(w.strip(':') for w in emoji['name'].lower().split())
        skip_words = name_words | {'object', 'other', 'symbol'}
        return [kw for kw in all_keywords if kw not in skip_words]

    def create_snippet(self, emoji_char: str, keyword: str, name: str, unicode_name: str) -> AlfredSnippetWithName:
        """Create a single Alfred snippet structure."""
        # Replace spaces with underscores in unicode_name for UID
        clean_unicode_name = unicode_name.replace(" ", "_")
        uid = f"emojipack-{keyword}-{clean_unicode_name}"

        return {
            "alfredsnippet": {
                "snippet": emoji_char,
                "uid": uid,
                "name": name,
                "keyword": keyword,  # No prefix/suffix - handled by info.plist
                "dontautoexpand": False
            },
            "_unicode_name": unicode_name,
        }

    def unicode_to_emoji(self, unified: str) -> str:
        """Convert unified Unicode codepoint to emoji character."""
        if not unified:
            return ""

        # Handle multiple codepoints separated by hyphens
        codepoints = unified.split("-")
        chars: list[str] = []

        for cp in codepoints:
            try:
                chars.append(chr(int(cp, 16)))
            except (ValueError, OverflowError):
                return ""

        return "".join(chars)

    def generate_snippets(self) -> list[AlfredSnippetWithName]:
        """Generate all emoji snippets."""
        self.emoji_data = self.fetch_emoji_data()
        snippets: list[AlfredSnippetWithName] = []

        for emoji in self.emoji_data:
            emoji_char = self.unicode_to_emoji(emoji["unified"])
            if not emoji_char:
                continue

            # Generate keywords for this emoji
            keywords = self.generate_keywords(emoji)

            # Create a snippet for each shortcode
            for short_name in emoji["short_names"]:
                name = emoji["name"].title()
                unicode_name = emoji["name"]
                snippet = self.create_snippet(
                    emoji_char=emoji_char,
                    keyword=short_name,
                    name=', '.join([f"{emoji_char} {name}"] + keywords),
                    unicode_name=unicode_name
                )
                snippets.append(snippet)

        return snippets

    def create_info_plist(self) -> str:
        """Create info.plist content with prefix and suffix settings."""
        return textwrap.dedent(f"""
            <?xml version="1.0" encoding="UTF-8"?>
            <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
            <plist version="1.0">
            <dict>
            	<key>snippetkeywordprefix</key>
            	<string>{escape(self.prefix)}</string>
            	<key>snippetkeywordsuffix</key>
            	<string>{escape(self.suffix)}</string>
            </dict>
            </plist>
            """).strip()

    def create_alfred_snippet_pack(self, snippets: list[AlfredSnippetWithName],
                                 output_path: Path) -> None:
        """Create the .alfredsnippets file."""
        # Create ZIP file directly using writestr
        with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
            # Add individual JSON files for each snippet
            for snippet in snippets:
                keyword = snippet["alfredsnippet"]["keyword"]
                unicode_name = snippet.get("_unicode_name", keyword.upper())

                # Create filename with keyword and unicode_name
                clean_unicode_name = unicode_name.strip().replace(" ", "_")
                filename = f"{keyword}-{clean_unicode_name}.json"

                # Remove temporary _unicode_name field before saving
                clean_snippet = {key: value for key, value in snippet.items() if key != "_unicode_name"}

                # Create JSON content and write directly to zip
                json_content = json.dumps(clean_snippet, ensure_ascii=False, indent=2)
                zf.writestr(filename, json_content)

            # Create and add info.plist file
            info_plist_content = self.create_info_plist()
            zf.writestr("info.plist", info_plist_content)


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
@click.option("--debug", "-d", is_flag=True, help="Enable debug mode for tracebacks.")
def main(prefix: str, suffix: str, output: str, max_emojis: int, debug: bool) -> None:
    """Generate Alfred emoji snippet pack from emoji database."""
    try:
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
    except BrokenPipeError:
        click.secho("Broken pipe", fg="red", bold=True, err=True)
    except Exception as e:
        if debug:
            raise
        click.echo(f"{click.style("Error:", fg="red", bold=True)} {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
