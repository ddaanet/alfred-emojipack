#!/usr/bin/env python3
"""
Test suite for Emoji Alfred Snippet Generator
"""

import json
import tempfile
import unittest
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path
from unittest.mock import MagicMock, patch

from emojipack_generator import EmojiData, EmojiSnippetGenerator


class BaseTestCase(unittest.TestCase):
    """Base test case with common setUp."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.generator: EmojiSnippetGenerator = EmojiSnippetGenerator()
        self.sample_emoji_data = [
            {
                "name": "GRINNING FACE",
                "unified": "1F600",
                "short_names": ["grinning", "grinning_face"],
                "category": "Smileys & Emotion",
                "subcategory": "face-smiling"
            },
            {
                "name": "THUMBS UP SIGN",
                "unified": "1F44D",
                "short_names": ["thumbsup", "thumbs_up"],
                "category": "People & Body",
                "subcategory": "hand-fingers-closed"
            }
        ]

    def assert_plist_settings(
            self, expected_prefix: str, expected_suffix: str,
            plist_content: str | None = None) -> None:
        """Utility method to test prefix and suffix in plist."""
        if plist_content is None:
            plist_content = self.generator.create_info_plist()

        # Parse XML to validate structure
        try:
            root = ET.fromstring(plist_content)
        except ET.ParseError as e:
            self.fail(f"Invalid XML in plist: {e}")

        # Find the dict element
        dict_elem = root.find("dict")
        self.assertIsNotNone(dict_elem)
        if dict_elem is None:
            self.fail("plist dict element not found")

        # Extract key-value pairs
        elements = list(dict_elem)
        pairs: dict[str, str] = {}
        for i in range(0, len(elements), 2):
            if (i + 1 < len(elements) and elements[i].tag == "key"
                    and elements[i + 1].tag == "string"):
                # ElementTree.text is None if the element is empty.
                value = elements[i + 1].text or ""
                key = elements[i].text
                assert key is not None
                pairs[key] = value

        self.assertEqual(pairs.get("snippetkeywordprefix"), expected_prefix)
        self.assertEqual(pairs.get("snippetkeywordsuffix"), expected_suffix)

    def assert_multiple_key_values(
            self, data: dict[str, object], expected_pairs: dict[str, object]) \
            -> None:
        """Utility method to test multiple key-value pairs at once."""
        actual_subset = {key: data[key] for key in expected_pairs.keys()}
        self.assertEqual(actual_subset, expected_pairs)


class TestUnicodeConversion(BaseTestCase):
    """Unicode to emoji conversion tests."""

    def test_basic_conversion(self) -> None:
        """Basic Unicode to emoji conversion works correctly."""
        self.assertEqual(self.generator.unicode_to_emoji("1F600"), "😀")
        self.assertEqual(self.generator.unicode_to_emoji("1F44D"), "👍")

    def test_complex_sequences(self) -> None:
        """Complex Unicode sequences convert properly."""
        self.assertEqual(
            self.generator.unicode_to_emoji("1F468-200D-1F4BB"), "👨‍💻")

    def test_edge_cases(self) -> None:
        """Unicode conversion raises errors for invalid input."""
        # Empty string should raise ValueError
        with self.assertRaises(ValueError):
            _ = self.generator.unicode_to_emoji("")

        # Invalid hex should raise ValueError
        with self.assertRaises(ValueError):
            _ = self.generator.unicode_to_emoji("INVALID")


class TestSnippetCreation(BaseTestCase):
    """Alfred snippet creation tests."""

    def test_snippet_structure(self) -> None:
        """Snippet structure and UID format are correct."""
        snippet = self.generator.create_snippet(
            "😀", "grinning", "😀 Grinning Face", "GRINNING FACE")

        alfred_snippet = snippet["alfredsnippet"]

        # Test individual fields to avoid type issues
        self.assertEqual(alfred_snippet["snippet"], "😀")
        self.assertEqual(alfred_snippet["keyword"], "grinning")
        self.assertEqual(alfred_snippet["name"], "😀 Grinning Face")
        self.assertEqual(alfred_snippet["uid"],
                         "emojipack-grinning-GRINNING_FACE")
        self.assertFalse(alfred_snippet["dontautoexpand"])


class TestKeywordGeneration(BaseTestCase):
    """Keyword extraction and generation tests."""

    def test_name_word_removal(self) -> None:
        """Name words are properly removed from subcategory keywords."""
        emoji: EmojiData = {
            "name": "GRINNING FACE",
            "subcategory": "face-smiling",
            "unified": "1F600",
            "short_names": ["grinning"],
            "category": "Smileys & Emotion"
        }
        keywords = self.generator.generate_keywords(emoji)
        # "face" removed because it's in the name, only "smiling" remains
        self.assertEqual(keywords, ["smiling"])

    def test_all_keywords_preserved(self) -> None:
        """Keywords are preserved when not in emoji name."""
        emoji: EmojiData = {
            "name": "THUMBS UP SIGN",
            "subcategory": "hand-fingers-closed",
            "unified": "1F44D",
            "short_names": ["thumbsup"],
            "category": "People & Body"
        }
        keywords = self.generator.generate_keywords(emoji)
        self.assertEqual(set(keywords), {"hand", "fingers", "closed"})

    def test_empty_keywords(self) -> None:
        """Empty keywords when all subcategory words are in name."""
        emoji: EmojiData = {
            "name": "KEYCAP: *",
            "subcategory": "keycap",
            "unified": "002A-FE0F-20E3",
            "short_names": ["keycap_star"],
            "category": "Symbols"
        }
        keywords = self.generator.generate_keywords(emoji)
        # "keycap" removed because it's in the name
        self.assertEqual(keywords, [])

    def test_filtered_words(self) -> None:
        """Generic words are filtered from keywords."""
        emoji: EmojiData = {
            "name": "SAMPLE ITEM",
            "subcategory": "test-object-other-symbol-valid",
            "unified": "1F600",
            "short_names": ["test"],
            "category": "Test"
        }
        keywords = self.generator.generate_keywords(emoji)
        # "object", "other", "symbol" filtered out
        self.assertEqual(set(keywords), {"test", "valid"})


class TestInfoPlistGeneration(BaseTestCase):
    """Info.plist XML generation tests."""

    def test_default_settings(self) -> None:
        """Default prefix and suffix settings work correctly."""
        self.assert_plist_settings(":", ":")

    def test_custom_settings(self) -> None:
        """Custom prefix and suffix settings work correctly."""
        self.generator = EmojiSnippetGenerator(prefix=",", suffix=".")
        self.assert_plist_settings(",", ".")

    def test_xml_escaping(self) -> None:
        """XML characters are properly escaped in plist."""
        self.generator = EmojiSnippetGenerator(prefix="<&", suffix=">&")
        self.assert_plist_settings("<&", ">&")

    def test_quote_handling(self) -> None:
        """Quotes and apostrophes are handled correctly in plist."""
        self.generator = EmojiSnippetGenerator(prefix='"test"', suffix="'end'")
        self.assert_plist_settings('"test"', "'end'")

    def test_empty_values(self) -> None:
        """Empty prefix and suffix values work correctly."""
        self.generator = EmojiSnippetGenerator(prefix="", suffix="")
        self.assert_plist_settings("", "")


class TestDataFetching(BaseTestCase):
    """Emoji data fetching tests."""

    @patch('requests.get')
    def test_successful_fetch(self, mock_get: MagicMock) -> None:
        """Emoji data is fetched successfully from API."""
        mock_response = MagicMock()
        mock_response.json.return_value = self.sample_emoji_data
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = self.generator.fetch_emoji_data()
        self.assertEqual(result, self.sample_emoji_data)


class TestEndToEnd(BaseTestCase):
    """End-to-end integration tests."""

    @patch('emojipack_generator.EmojiSnippetGenerator.fetch_emoji_data')
    def test_complete_snippet_pack_generation(self, mock_fetch: MagicMock) -> None:
        """Complete snippet pack generation works correctly."""
        mock_fetch.return_value = self.sample_emoji_data

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "test-pack.alfredsnippets"

            # Generate and create the snippet pack
            generator = EmojiSnippetGenerator(prefix="[", suffix="]")
            snippets = generator.generate_snippets()
            generator.create_alfred_snippet_pack(snippets, output_path)

            # Verify file creation and structure
            self.assertTrue(output_path.exists())

            with zipfile.ZipFile(output_path, 'r') as zip_file:
                file_list = zip_file.namelist()

                # Verify essential files exist
                self.assertIn('info.plist', file_list)

                # Verify plist content using utility function
                with zip_file.open('info.plist') as plist_file:
                    plist_content = plist_file.read().decode('utf-8')
                    self.assert_plist_settings("[", "]", plist_content)

                # Test precise file names - compare sorted lists
                json_files = sorted(
                    [f for f in file_list if f.endswith('.json')])
                expected_files = sorted([
                    'grinning-GRINNING_FACE.json',
                    'grinning_face-GRINNING_FACE.json',
                    'thumbsup-THUMBS_UP_SIGN.json',
                    'thumbs_up-THUMBS_UP_SIGN.json'])

                self.assertEqual(json_files, expected_files)

                # Test precise content of a specific snippet file
                test_snippet_file = 'grinning-GRINNING_FACE.json'
                with zip_file.open(test_snippet_file) as snippet_file:
                    snippet_data = json.load(snippet_file)
                    alfred_snippet = snippet_data['alfredsnippet']

                    # Test precise expected values for this specific snippet
                    expected_snippet_content = {
                        "snippet": "😀",
                        "keyword": "grinning",
                        "uid": "emojipack-grinning-GRINNING_FACE",
                        "name": "😀 Grinning Face, smiling",
                        "dontautoexpand": False}

                    self.assert_multiple_key_values(
                        alfred_snippet, expected_snippet_content)


if __name__ == "__main__":
    _ = unittest.main()
