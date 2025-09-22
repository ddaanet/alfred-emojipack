#!/usr/bin/env python3
"""
Alfred Emoji Snippet Pack Generator

Fetches emoji data from Emojibase and creates Alfred snippet packs
with Unicode names, shortcodes, and keywords for searchability.
"""

import json
import click
import requests
from pathlib import Path
import uuid
from typing import Dict, List, Any
import unittest


def fetch_emoji_data(locale: str = "en") -> List[Dict[str, Any]]:
    """Fetch emoji data from Emojibase CDN."""
    url = f"https://cdn.jsdelivr.net/npm/emojibase-data@latest/{locale}/compact.json"
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return response.json()


def fetch_shortcodes(locale: str = "en", preset: str = "github") -> Dict[str, List[str]]:
    """Fetch shortcode mappings from Emojibase CDN."""
    url = f"https://cdn.jsdelivr.net/npm/emojibase-data@latest/{locale}/shortcodes/{preset}.json"
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        click.echo(f"Warning: Could not fetch {preset} shortcodes", err=True)
        return {}


def create_alfred_snippet(emoji: str, shortcode: str, name: str, keywords: List[str], uid: str) -> Dict[str, Any]:
    """Create an Alfred snippet object."""
    keyword_str = " ".join(keywords) if keywords else ""

    return {
        "alfredsnippet": {
            "snippet": emoji,
            "uid": uid,
            "name": name,
            "keyword": f"{shortcode} {keyword_str}".strip()
        }
    }


def generate_alfred_snippets(
    emoji_data: List[Dict[str, Any]],
    shortcode_data: Dict[str, List[str]],
    max_emojis: int = None
) -> List[Dict[str, Any]]:
    """Generate Alfred snippets from emoji data."""
    snippets = []

    for i, emoji in enumerate(emoji_data):
        if max_emojis and i >= max_emojis:
            break

        emoji_char = emoji.get("unicode", "")
        if not emoji_char:
            continue

        # Get primary shortcode - ensure it's a list
        shortcodes = emoji.get("shortcodes", [])
        if isinstance(shortcodes, str):
            shortcodes = [shortcodes]
        elif not isinstance(shortcodes, list):
            shortcodes = []

        primary_shortcode = shortcodes[0] if shortcodes else ""

        # Try to get additional shortcodes from shortcode data
        hexcode = emoji.get("hexcode", "")
        additional_shortcodes = shortcode_data.get(hexcode, [])
        if isinstance(additional_shortcodes, str):
            additional_shortcodes = [additional_shortcodes]
        elif not isinstance(additional_shortcodes, list):
            additional_shortcodes = []

        # Combine all shortcodes
        all_shortcodes = list(set(shortcodes + additional_shortcodes))

        # Get name and tags - ensure tags is a list
        name = emoji.get("annotation", f"Emoji {emoji_char}")
        tags = emoji.get("tags", [])
        if isinstance(tags, str):
            tags = [tags]
        elif not isinstance(tags, list):
            tags = []

        # Create keywords list
        keywords = all_shortcodes + tags

        # Generate unique ID
        uid = str(uuid.uuid4())

        snippet = create_alfred_snippet(
            emoji=emoji_char,
            shortcode=primary_shortcode,
            name=name,
            keywords=keywords,
            uid=uid
        )

        snippets.append(snippet)

    return snippets


@click.command()
@click.option("--locale", "-l", default="en", help="Locale for emoji data (default: en)")
@click.option("--shortcodes", "-s", default="github", help="Shortcode preset (github, cldr, emojibase)")
@click.option("--output", "-o", type=click.Path(), help="Output file path")
@click.option("--max-emojis", "-m", type=int, help="Maximum number of emojis to include")
@click.option("--bundle-name", "-n", default="Emoji Pack", help="Alfred snippet bundle name")
@click.option("--debug", "-d", is_flag=True, help="Enable debug output")
def main(locale: str, shortcodes: str, output: str, max_emojis: int, bundle_name: str, debug: bool):
    """Generate Alfred emoji snippet pack from Emojibase data."""
    click.echo(f"Fetching emoji data for locale: {locale}")

    try:
        # Fetch data
        emoji_data = fetch_emoji_data(locale)
        shortcode_data = fetch_shortcodes(locale, shortcodes)

        click.echo(f"Fetched {len(emoji_data)} emojis")

        if debug and emoji_data:
            click.echo(f"Sample emoji data: {emoji_data[0]}")
            if shortcode_data:
                sample_key = next(iter(shortcode_data.keys()))
                click.echo(f"Sample shortcode data: {sample_key} -> {shortcode_data[sample_key]}")

        # Generate snippets
        snippets = generate_alfred_snippets(emoji_data, shortcode_data, max_emojis)

        # Create Alfred bundle structure
        bundle = {
            "alfredsnippet": {
                "description": f"Emoji snippets generated from Emojibase ({locale})",
                "name": bundle_name,
                "snippets": [snippet["alfredsnippet"] for snippet in snippets]
            }
        }

        # Determine output path
        if not output:
            output = f"emoji-{locale}-{shortcodes}.alfredsnippets"

        # Write output
        output_path = Path(output)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(bundle, f, ensure_ascii=False, indent=2)

        click.echo(f"Generated {len(snippets)} emoji snippets")
        click.echo(f"Saved to: {output_path}")
        click.echo(f"Import this file into Alfred via Snippets > Import")

    except requests.RequestException as e:
        click.echo(f"Error fetching data: {e}", err=True)
        raise click.Abort()
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        if debug:
            import traceback
            traceback.print_exc()
        raise click.Abort()


class TestEmojiGenerator(unittest.TestCase):
    """Test suite for emoji generator functions."""

    def setUp(self):
        """Set up test data."""
        self.sample_emoji = {
            "unicode": "😀",
            "hexcode": "1F600",
            "annotation": "grinning face",
            "shortcodes": ["grinning"],
            "tags": ["face", "smile", "happy"]
        }

        self.sample_shortcodes = {
            "1F600": ["grinning", "smile"]
        }

    def test_create_alfred_snippet(self):
        """Test Alfred snippet creation."""
        snippet = create_alfred_snippet(
            emoji="😀",
            shortcode="grinning",
            name="grinning face",
            keywords=["face", "smile"],
            uid="test-uid"
        )

        self.assertEqual(snippet["alfredsnippet"]["snippet"], "😀")
        self.assertEqual(snippet["alfredsnippet"]["name"], "grinning face")
        self.assertIn("grinning", snippet["alfredsnippet"]["keyword"])

    def test_generate_alfred_snippets(self):
        """Test snippet generation."""
        snippets = generate_alfred_snippets(
            [self.sample_emoji],
            self.sample_shortcodes,
            max_emojis=1
        )

        self.assertEqual(len(snippets), 1)
        self.assertEqual(snippets[0]["alfredsnippet"]["snippet"], "😀")

    def test_max_emojis_limit(self):
        """Test emoji limit functionality."""
        emoji_list = [self.sample_emoji] * 5
        snippets = generate_alfred_snippets(emoji_list, {}, max_emojis=3)

        self.assertEqual(len(snippets), 3)


if __name__ == "__main__":
    main()
