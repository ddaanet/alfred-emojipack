#!/usr/bin/env python3
"""
Unified test runner for Emoji Alfred Snippet Generator
"""

import json
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch, MagicMock
import requests

from emoji_alfred_generator import EmojiSnippetGenerator


class TestEmojiGenerator(unittest.TestCase):
    """Comprehensive test suite for emoji generator."""

    def setUp(self):
        """Set up test fixtures."""
        self.generator = EmojiSnippetGenerator(prefix=";", suffix="")
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

    def test_unicode_conversion_basic(self):
        """Test Unicode to emoji conversion."""
        # Basic conversion
        self.assertEqual(self.generator.unicode_to_emoji("1F600"), "😀")
        self.assertEqual(self.generator.unicode_to_emoji("1F44D"), "👍")

        # Complex sequences
        self.assertEqual(self.generator.unicode_to_emoji("1F468-200D-1F4BB"), "👨‍💻")

        # Edge cases
        self.assertEqual(self.generator.unicode_to_emoji(""), "")
        self.assertEqual(self.generator.unicode_to_emoji("INVALID"), "")

    def test_snippet_creation(self):
        """Test snippet structure and UID format."""
        snippet = self.generator.create_snippet("😀", "grinning", "😀 Grinning Face", "GRINNING FACE")

        alfred_snippet = snippet["alfredsnippet"]
        self.assertEqual(alfred_snippet["snippet"], "😀")
        self.assertEqual(alfred_snippet["keyword"], "grinning")
        self.assertEqual(alfred_snippet["name"], "😀 Grinning Face")
        self.assertEqual(alfred_snippet["uid"], "emojipack-grinning-GRINNING_FACE")
        self.assertFalse(alfred_snippet["dontautoexpand"])

    def test_keyword_generation(self):
        """Test keyword extraction from emoji data."""
        # Test with GRINNING FACE - subcategory "face-smiling"
        # Name words "grinning" and "face" should be removed
        emoji = self.sample_emoji_data[0]
        keywords = self.generator.generate_keywords(emoji)

        # Should only contain "smiling" since "face" is in the name
        self.assertEqual(keywords, ["smiling"])

        # Test with THUMBS UP SIGN - subcategory "hand-fingers-closed"
        # Name words "thumbs", "up", "sign" not in subcategory, so all keywords remain
        emoji2 = self.sample_emoji_data[1]
        keywords2 = self.generator.generate_keywords(emoji2)
        self.assertEqual(set(keywords2), {"hand", "fingers", "closed"})

        # Test special case: Keycap with name containing words from subcategory
        keycap_emoji = {
            "name": "KEYCAP: *",
            "subcategory": "keycap",
            "unified": "002A-FE0F-20E3",
            "short_names": ["keycap_star"],
            "category": "Symbols"
        }
        keywords3 = self.generator.generate_keywords(keycap_emoji)
        self.assertEqual(keywords3, [])  # "keycap" removed because it's in the name

        # Test filtering of "object", "other", "symbol"
        test_emoji = {
            "name": "SAMPLE ITEM",
            "subcategory": "test-object-other-symbol-valid",
            "unified": "1F600",
            "short_names": ["test"],
            "category": "Test"
        }
        keywords4 = self.generator.generate_keywords(test_emoji)
        self.assertEqual(set(keywords4), {"test", "valid"})  # object, other, symbol filtered out

    def test_info_plist_generation(self):
        """Test info.plist XML generation."""
        # Default settings
        plist_content = self.generator.create_info_plist()
        self.assertIn("snippetkeywordprefix", plist_content)
        self.assertIn("snippetkeywordsuffix", plist_content)
        self.assertIn("<string>;</string>", plist_content)

        # Custom settings
        custom_generator = EmojiSnippetGenerator(prefix=":", suffix=":")
        plist_content = custom_generator.create_info_plist()
        self.assertEqual(plist_content.count("<string>:</string>"), 2)

    def test_info_plist_xml_escaping(self):
        """Test that prefix and suffix are properly XML escaped."""
        # Test XML characters that need escaping
        generator_with_xml_chars = EmojiSnippetGenerator(prefix="<&", suffix=">&")
        plist_content = generator_with_xml_chars.create_info_plist()

        # Should contain escaped versions
        self.assertIn("<string>&lt;&amp;</string>", plist_content)
        self.assertIn("<string>&gt;&amp;</string>", plist_content)

        # Should not contain unescaped versions
        self.assertNotIn("<string><&</string>", plist_content)
        self.assertNotIn("<string>>&</string>", plist_content)

        # Test quotes and apostrophes - xml.sax.saxutils.escape does NOT escape them
        generator_with_quotes = EmojiSnippetGenerator(prefix='"test"', suffix="'end'")
        plist_content = generator_with_quotes.create_info_plist()
        self.assertIn('<string>"test"</string>', plist_content)
        self.assertIn("<string>'end'</string>", plist_content)

        # Test empty values
        generator_empty = EmojiSnippetGenerator(prefix="", suffix="")
        plist_content = generator_empty.create_info_plist()
        self.assertEqual(plist_content.count("<string></string>"), 2)

    @patch('requests.get')
    def test_emoji_data_fetch(self, mock_get):
        """Test emoji data fetching."""
        mock_response = MagicMock()
        mock_response.json.return_value = self.sample_emoji_data
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = self.generator.fetch_emoji_data()
        self.assertEqual(result, self.sample_emoji_data)


def run_functionality_test():
    """Quick functionality verification."""
    print("Running functionality test...")

    try:
        generator = EmojiSnippetGenerator(prefix=";")

        # Test basic functions
        emoji_char = generator.unicode_to_emoji("1F600")
        assert emoji_char == "😀", f"Unicode conversion failed: {emoji_char}"

        snippet = generator.create_snippet("😀", "grinning", "😀 Grinning Face", "GRINNING FACE")
        assert snippet["alfredsnippet"]["uid"] == "emojipack-grinning-GRINNING_FACE", "UID format incorrect"
        assert snippet["alfredsnippet"]["keyword"] == "grinning", "Keyword format incorrect"

        plist = generator.create_info_plist()
        assert "snippetkeywordprefix" in plist, "Info.plist missing prefix"

        print("✓ All functionality tests passed!")
        return True

    except Exception as e:
        print(f"✗ Functionality test failed: {e}")
        return False


def main():
    """Main test runner with both unit tests and functionality tests."""
    print("=== Emoji Alfred Generator Test Suite ===")

    # Run functionality test first
    if not run_functionality_test():
        return 1

    print("\nRunning unit tests...")

    # Run unit tests
    suite = unittest.TestLoader().loadTestsFromTestCase(TestEmojiGenerator)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    if result.wasSuccessful():
        print("\n✓ All tests passed!")
        return 0
    else:
        print("\n✗ Some tests failed!")
        return 1


if __name__ == "__main__":
    exit(main())
