#!/usr/bin/env python3
"""
Test suite for Emoji Alfred Snippet Generator
"""

import json
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch, MagicMock

# Import the main module (ensure emoji_alfred_generator.py is in the same directory)
try:
    from emoji_alfred_generator import EmojiSnippetGenerator
except ImportError:
    import sys
    sys.path.append('.')
    from emoji_alfred_generator import EmojiSnippetGenerator


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

        snippet = self.generator.create_snippet(emoji_char, keyword, name)

        # Check structure
        self.assertIn("alfredsnippet", snippet)
        alfred_snippet = snippet["alfredsnippet"]

        self.assertEqual(alfred_snippet["snippet"], emoji_char)
        self.assertEqual(alfred_snippet["keyword"], ";grinning")
        self.assertEqual(alfred_snippet["name"], name)
        self.assertIsInstance(alfred_snippet["uid"], str)
        self.assertFalse(alfred_snippet["dontautoexpand"])

    @patch('emoji_alfred_generator.requests.get')
    def test_fetch_emoji_data(self, mock_get):
        """Test emoji data fetching."""
        mock_response = MagicMock()
        mock_response.json.return_value = self.sample_emoji_data
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = self.generator.fetch_emoji_data()

        self.assertEqual(result, self.sample_emoji_data)
        mock_get.assert_called_once()

    def test_generate_snippets_integration(self):
        """Test snippet generation integration."""
        # Mock the data fetch
        self.generator.emoji_data = self.sample_emoji_data
        with patch.object(self.generator, 'fetch_emoji_data', return_value=self.sample_emoji_data):
            snippets = self.generator.generate_snippets()

        # Should generate multiple snippets (one per shortcode)
        expected_count = sum(len(emoji.get("short_names", [])) for emoji in self.sample_emoji_data)
        self.assertEqual(len(snippets), expected_count)

        # Check first snippet structure
        first_snippet = snippets[0]
        self.assertIn("alfredsnippet", first_snippet)
        self.assertTrue(first_snippet["alfredsnippet"]["keyword"].startswith(";"))

    def test_create_alfred_snippet_pack(self):
        """Test Alfred snippet pack creation."""
        # Create sample snippets
        snippets = [
            {
                "alfredsnippet": {
                    "snippet": "😀",
                    "uid": "TEST-UUID-1",
                    "name": "😀 Grinning Face",
                    "keyword": ";grinning",
                    "dontautoexpand": False
                }
            },
            {
                "alfredsnippet": {
                    "snippet": "👍",
                    "uid": "TEST-UUID-2",
                    "name": "👍 Thumbs Up",
                    "keyword": ";thumbsup",
                    "dontautoexpand": False
                }
            }
        ]

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "test.alfredsnippets"

            self.generator.create_alfred_snippet_pack(snippets, output_path)

            # Verify file was created
            self.assertTrue(output_path.exists())

            # Verify it's a valid ZIP
            with zipfile.ZipFile(output_path, 'r') as zf:
                files = zf.namelist()
                self.assertEqual(len(files), 2)

                # Check first file content
                with zf.open(files[0]) as f:
                    content = json.loads(f.read().decode('utf-8'))
                    self.assertIn("alfredsnippet", content)


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

        snippet = generator.create_snippet("😀", "grinning", "Grinning")

        self.assertEqual(snippet["alfredsnippet"]["keyword"], "!grinning")


def run_tests():
    """Run all tests."""
    unittest.main(verbosity=2)


if __name__ == "__main__":
    run_tests()
