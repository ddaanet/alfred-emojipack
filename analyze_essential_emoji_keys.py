#!/usr/bin/env python3
"""
Essential Emoji Data Key Analysis Script

Analyzes emoji.json from iamcal/emoji-data to identify which keys are essential
for the emoji generator and suggests an optimized EmojiData structure.
"""

import json
from collections import Counter
from typing import Any, Dict, List, Set

import requests


def fetch_emoji_data() -> List[Dict[str, Any]]:
    """Fetch emoji data from iamcal/emoji-data repository."""
    url = "https://raw.githubusercontent.com/iamcal/emoji-data/master/emoji.json"
    print(f"Fetching emoji data from: {url}")
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return response.json()


def analyze_essential_fields(emoji_data: List[Dict[str, Any]]) -> None:
    """Analyze only the essential fields used by the emoji generator."""

    # Fields used by the current emoji generator
    essential_fields = {
        'unified': 'Unicode codepoints for the emoji',
        'name': 'Official emoji name',
        'category': 'Main category classification',
        'subcategory': 'Sub-category classification',
        'short_names': 'List of shortcode names'
    }

    total_emojis = len(emoji_data)
    print(f"Analyzing {total_emojis} emoji entries for essential fields...\n")

    # Analyze each essential field
    field_analysis = {}

    for field_name, description in essential_fields.items():
        print(f"Analyzing '{field_name}' ({description}):")
        print("-" * 50)

        present_count = 0
        empty_count = 0
        type_counts = Counter()
        sample_values = []

        for emoji in emoji_data:
            if field_name in emoji:
                present_count += 1
                value = emoji[field_name]

                # Check if empty
                if not value or (isinstance(value, list) and len(value) == 0):
                    empty_count += 1
                else:
                    # Collect sample values (first 3 non-empty)
                    if len(sample_values) < 3:
                        sample_values.append(value)

                # Track types
                if isinstance(value, list):
                    if value:
                        item_type = type(value[0]).__name__
                        type_counts[f"list[{item_type}]"] += 1
                    else:
                        type_counts["list[empty]"] += 1
                else:
                    type_counts[type(value).__name__] += 1

        # Store analysis
        field_analysis[field_name] = {
            'present_count': present_count,
            'empty_count': empty_count,
            'type_counts': type_counts,
            'sample_values': sample_values,
            'description': description
        }

        # Print field analysis
        presence_pct = (present_count / total_emojis) * 100
        empty_pct = (empty_count / total_emojis) * 100 if present_count > 0 else 0

        print(f"  Present in: {present_count}/{total_emojis} ({presence_pct:.1f}%)")
        print(f"  Empty/None: {empty_count}/{present_count} ({empty_pct:.1f}%)")
        print(f"  Types: {dict(type_counts)}")
        if sample_values:
            print(f"  Samples: {sample_values}")
        print()

    # Generate recommendations
    print("=" * 60)
    print("RECOMMENDATIONS FOR EmojiData STRUCTURE")
    print("=" * 60)

    print("\n# Current structure analysis:")
    required_fields = []
    optional_fields = []

    for field_name, analysis in field_analysis.items():
        presence_pct = (analysis['present_count'] / total_emojis) * 100
        empty_pct = (analysis['empty_count'] / analysis['present_count']) * 100 if analysis['present_count'] > 0 else 0

        # Determine if field should be required or optional
        if presence_pct == 100.0 and empty_pct < 5.0:  # Present in all, rarely empty
            required_fields.append(field_name)
            status = "REQUIRED"
        elif presence_pct == 100.0 and empty_pct >= 5.0:  # Present in all, sometimes empty
            optional_fields.append(field_name)
            status = "OPTIONAL (often empty)"
        elif presence_pct < 100.0:  # Not always present
            optional_fields.append(field_name)
            status = "OPTIONAL (sometimes missing)"
        else:
            required_fields.append(field_name)
            status = "REQUIRED"

        print(f"  {field_name}: {status}")
        print(f"    - Present: {presence_pct:.1f}%, Empty: {empty_pct:.1f}%")

    # Generate TypedDict structure
    print(f"\n{'=' * 60}")
    print("SUGGESTED EmojiData TYPEDDICT STRUCTURE")
    print("=" * 60)

    print("""
# Option 1: Conservative approach (all fields optional for safety)
class EmojiData(TypedDict, total=False):
    unified: str
    name: str
    category: str
    subcategory: str
    short_names: list[str]

# Option 2: Optimized approach based on analysis
class EmojiDataRequired(TypedDict):""")

    for field_name in required_fields:
        analysis = field_analysis[field_name]
        most_common_type = analysis['type_counts'].most_common(1)[0][0]
        print(f"    {field_name}: {most_common_type}")

    if not required_fields:
        print("    pass  # No consistently reliable required fields")

    print("""
class EmojiData(EmojiDataRequired, total=False):""")

    for field_name in optional_fields:
        analysis = field_analysis[field_name]
        most_common_type = analysis['type_counts'].most_common(1)[0][0]
        print(f"    {field_name}: {most_common_type}")

    if not optional_fields:
        print("    pass  # No optional fields")

    # Practical recommendations
    print(f"\n{'=' * 60}")
    print("PRACTICAL RECOMMENDATIONS")
    print("=" * 60)

    print("""
For your emoji generator, consider:

1. DEFENSIVE PROGRAMMING: Always use .get() with defaults
   - unified = emoji.get("unified", "")
   - name = emoji.get("name", "unknown")
   - short_names = emoji.get("short_names", [])

2. VALIDATION: Check for empty/invalid values before processing
   - Skip emojis with empty unified codes
   - Skip emojis with empty short_names lists
   - Use fallback names when name is empty

3. ERROR HANDLING: Handle missing or malformed data gracefully
   - Log warnings for unexpected data formats
   - Continue processing other emojis when one fails""")


def main() -> None:
    """Main function to run the essential fields analysis."""
    try:
        emoji_data = fetch_emoji_data()
        analyze_essential_fields(emoji_data)

        print(f"\n{'=' * 60}")
        print("ANALYSIS COMPLETE")
        print("=" * 60)
        print("Review the recommendations above to optimize your EmojiData structure.")

    except Exception as e:
        print(f"Error: {e}")
        return


if __name__ == "__main__":
    main()
