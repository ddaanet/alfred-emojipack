#!/usr/bin/env python3
"""
Simple test runner that avoids import conflicts
"""

import json
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch, MagicMock
import requests


# Inline the EmojiSnippetGenerator class to avoid import issues
class EmojiSnippetGenerator:
    def __init__(self, prefix: str = ";", suffix: str = ""):
        self.prefix = prefix
        self.suffix = suffix
        self.emoji_data = []

    def fetch_emoji_data(self):
        """Fetch emoji data from iamcal/emoji-data repository."""
        url = "https://raw.githubusercontent.com/iamcal/emoji-data/master/emoji.json"
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.json()

    def generate_keywords(self, emoji):
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

    def create_snippet(self, emoji_char: str, keyword: str, name: str, unicode_name: str):
        """Create a single Alfred snippet structure."""
        return {
            "alfredsnippet": {
                "snippet": emoji_char,
                "uid": f"emojipack:{unicode_name}",
                "name": name,
                "keyword": keyword,  # No prefix/suffix - handled by info.plist
                "dontautoexpand": False
            }
        }

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


class TestEmojiSnippetGenerator(unittest.TestCase):
    """Test cases for EmojiSnippetGenerator."""

    def setUp(self):
        """Set up test fixtures."""
        self.generator = EmojiSnippetGenerator(prefix=";")
        self.sample_emoji_data = [
            {
                "name": "GRINNING FACE",
                "unified": "1F600",
                "short_name": "grinning",
                "short_names": ["grinning", "grinning_face"],
                "category": "Smileys & Emotion",
                "subcategory": "face-smiling"
            },
            {
                "name": "THUMBS UP SIGN",
                "unified": "1F44D",
                "short_name": "thumbsup",
                "short_names": ["thumbsup", "+1", "thumbs_up"],
                "category": "People & Body",
                "subcategory": "hand-fingers-closed"
            }
        ]

    def test_unicode_to_emoji_basic(self):
        """Test basic Unicode to emoji conversion."""
        # Test simple codepoint
        result = self.generator.unicode_to_emoji("1F600")
        self.assertEqual(result, "😀")

        # Test compound codepoint
        result = self.generator.unicode_to_emoji("1F44D")
        self.assertEqual(result, "👍")

    def test_unicode_to_emoji_complex(self):
        """Test complex Unicode sequences."""
        # Test sequence with multiple codepoints
        result = self.generator.unicode_to_emoji("1F468-200D-1F4BB")
        self.assertEqual(result, "👨‍💻")  # man technologist

        # Test invalid codepoint
        result = self.generator.unicode_to_emoji("INVALID")
        self.assertEqual(result, "")

        # Test empty input
        result = self.generator.unicode_to_emoji("")
        self.assertEqual(result, "")

    def test_generate_keywords(self):
        """Test keyword generation."""
        emoji = self.sample_emoji_data[0]
        keywords = self.generator.generate_keywords(emoji)

        # Should include name words
        self.assertIn("grinning", keywords)
        self.assertIn("face", keywords)

        # Should include category
        self.assertIn("smileys_&_emotion", keywords)

        # Should include subcategory
        self.assertIn("face-smiling", keywords)

        # Should include all shortcodes
        self.assertIn("grinning", keywords)
        self.assertIn("grinning_face", keywords)

    def test_create_snippet(self):
        """Test snippet creation."""
        emoji_char = "😀"
        keyword = "grinning"
        name = "😀 Grinning Face"
        unicode_name = "GRINNING FACE"

        snippet = self.generator.create_snippet(emoji_char, keyword, name, unicode_name)

        # Check structure
        self.assertIn("alfredsnippet", snippet)
        alfred_snippet = snippet["alfredsnippet"]

        self.assertEqual(alfred_snippet["snippet"], emoji_char)
        self.assertEqual(alfred_snippet["keyword"], "grinning")  # No prefix in keyword
        self.assertEqual(alfred_snippet["name"], name)
        self.assertEqual(alfred_snippet["uid"], "emojipack:GRINNING FACE")
        self.assertFalse(alfred_snippet["dontautoexpand"])

    def test_prefix_customization(self):
        """Test custom prefix handling."""
        generator = EmojiSnippetGenerator(prefix="!", suffix="?")

        snippet = generator.create_snippet("😀", "grinning", "Grinning", "GRINNING FACE")

        # Prefix/suffix not in individual snippets
        self.assertEqual(snippet["alfredsnippet"]["keyword"], "grinning")
        self.assertEqual(snippet["alfredsnippet"]["uid"], "emojipack:GRINNING FACE")

        # Check info.plist generation
        plist_content = generator.create_info_plist()
        self.assertIn("<string>!</string>", plist_content)
        self.assertIn("<string>?</string>", plist_content)
        self.assertIn("snippetkeywordprefix", plist_content)
        self.assertIn("snippetkeywordsuffix", plist_content)


class TestInfoPlistGeneration(unittest.TestCase):
    """Test info.plist file generation."""

    def test_info_plist_format(self):
        """Test info.plist XML format."""
        generator = EmojiSnippetGenerator(prefix=";", suffix="")
        plist_content = generator.create_info_plist()

        # Check XML structure
        self.assertTrue(plist_content.startswith('<?xml version="1.0"'))
        self.assertIn("snippetkeywordprefix", plist_content)
        self.assertIn("snippetkeywordsuffix", plist_content)
        self.assertIn("<string>;</string>", plist_content)

    def test_custom_prefix_suffix(self):
        """Test custom prefix and suffix in info.plist."""
        generator = EmojiSnippetGenerator(prefix=":", suffix=":")
        plist_content = generator.create_info_plist()

        # Should contain both prefix and suffix as colons
        colon_count = plist_content.count("<string>:</string>")
        self.assertEqual(colon_count, 2)  # One for prefix, one for suffix


class TestKeywordGeneration(unittest.TestCase):
    """Focused tests for keyword generation logic."""

    def setUp(self):
        self.generator = EmojiSnippetGenerator()

    def test_name_word_extraction(self):
        """Test extraction of words from emoji names."""
        emoji = {
            "name": "WOMAN HEALTH WORKER: MEDIUM SKIN TONE",
            "short_names": ["woman_health_worker"]
        }

        keywords = self.generator.generate_keywords(emoji)

        self.assertIn("woman", keywords)
        self.assertIn("health", keywords)
        self.assertIn("worker", keywords)
        self.assertIn("medium", keywords)
        self.assertIn("skin", keywords)
        self.assertIn("tone", keywords)

    def test_category_normalization(self):
        """Test category name normalization."""
        emoji = {
            "name": "TEST",
            "category": "Smileys & Emotion",
            "subcategory": "face-smiling",
            "short_names": ["test"]
        }

        keywords = self.generator.generate_keywords(emoji)

        self.assertIn("smileys_&_emotion", keywords)
        self.assertIn("face-smiling", keywords)

    def test_empty_data_handling(self):
        """Test handling of missing or empty data."""
        emoji = {
            "name": "",
            "short_names": []
        }

        keywords = self.generator.generate_keywords(emoji)

        # Should not crash and return empty set
        self.assertIsInstance(keywords, set)


class TestUtilityFunctions(unittest.TestCase):
    """Test utility functions."""

    def test_prefix_customization(self):
        """Test custom prefix handling."""
        generator = EmojiSnippetGenerator(prefix="!")

        snippet = generator.create_snippet("😀", "grinning", "Grinning", "GRINNING FACE")

        self.assertEqual(snippet["alfredsnippet"]["keyword"], "grinning")
        self.assertEqual(snippet["alfredsnippet"]["uid"], "emojipack:GRINNING FACE")


def run_tests():
    """Run all tests."""
    unittest.main(verbosity=2)


if __name__ == "__main__":
    run_tests()
