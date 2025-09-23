#!/usr/bin/env python3
"""
Emoji Data Key Analysis Script

Analyzes emoji.json from iamcal/emoji-data to identify which keys are always present
and which are optional in the emoji data structure.

Note: This script contains intentional type: ignore comments for JSON data handling.
The remaining mypy warnings about 'Any' types are inherent to analyzing arbitrary
JSON structures and are acceptable for this analysis tool.
"""

from collections import Counter
import requests


def fetch_emoji_data() -> list[dict[str, object]]:
    """Fetch emoji data from iamcal/emoji-data repository."""
    url = "https://raw.githubusercontent.com/iamcal/emoji-data/master/emoji.json"
    print(f"Fetching emoji data from: {url}")
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    # JSON response returns Any - unavoidable for dynamic data analysis
    return response.json()  # type: ignore[no-any-return, return-value]


def analyze_keys(emoji_data: list[dict[str, object]]) -> None:
    """Analyze keys in emoji data to identify required vs optional fields."""
    total_emojis = len(emoji_data)
    print(f"Analyzing {total_emojis} emoji entries...\n")

    # Count occurrences of each key
    key_counts: Counter[str] = Counter()
    all_keys: set[str] = set()

    # Track value types for each key
    key_types: dict[str, set[str]] = {}

    for emoji in emoji_data:
        emoji_keys = emoji.keys()
        all_keys.update(emoji_keys)

        for key in emoji_keys:
            key_counts[key] += 1

            # Track value types
            if key not in key_types:
                key_types[key] = set()

            value = emoji[key]
            if isinstance(value, list):
                if value:  # Non-empty list
                    item_type = type(value[0]).__name__
                    key_types[key].add(f"list[{item_type}]")
                else:  # Empty list
                    key_types[key].add("list[empty]")
            else:
                # Dynamic type inspection - inherently involves unknown types
                type_name = type(value).__name__
                key_types[key].add(type_name)  # type: ignore[arg-type, misc]

    # Categorize keys
    always_present: list[tuple[str, int, float, list[str]]] = []
    sometimes_present: list[tuple[str, int, float, list[str]]] = []

    for key in sorted(all_keys):
        count = key_counts[key]
        percentage = (count / total_emojis) * 100
        types = sorted(key_types[key])

        if count == total_emojis:
            always_present.append((key, count, percentage, types))
        else:
            sometimes_present.append((key, count, percentage, types))

    # Print results
    print("=" * 60)
    print("ALWAYS PRESENT KEYS (100% of emojis)")
    print("=" * 60)
    for key, count, percentage, types in always_present:
        print(f"{key:15} | {count:5} ({percentage:5.1f}%) | Types: {', '.join(types)}")

    print(f"\n{'=' * 60}")
    print("SOMETIMES PRESENT KEYS (< 100% of emojis)")
    print("=" * 60)
    for key, count, percentage, types in sometimes_present:
        print(f"{key:15} | {count:5} ({percentage:5.1f}%) | Types: {', '.join(types)}")

    # Generate TypedDict suggestions
    print(f"\n{'=' * 60}")
    print("TYPEDDICT STRUCTURE SUGGESTIONS")
    print("=" * 60)

    print("\n# Required fields (always present):")
    print("class EmojiDataRequired(TypedDict):")
    if always_present:
        for key, _, _, types in always_present:
            # Simplify type annotation
            if len(types) == 1:
                type_str = types[0]
                if type_str.startswith("list[") and type_str != "list[empty]":
                    type_str = type_str.replace("list[", "list[").replace("]", "]")
                elif type_str == "list[empty]":
                    type_str = "list[str]"  # Assume string list for empty
            else:
                type_str = " | ".join(types)
            print(f'    {key}: {type_str}')
    else:
        print("    pass  # No always-present fields")

    print("\n# Optional fields (sometimes present):")
    print("class EmojiData(EmojiDataRequired, total=False):")
    if sometimes_present:
        for key, _, _, types in sometimes_present:
            # Simplify type annotation
            if len(types) == 1:
                type_str = types[0]
                if type_str.startswith("list[") and type_str != "list[empty]":
                    type_str = type_str.replace("list[", "list[").replace("]", "]")
                elif type_str == "list[empty]":
                    type_str = "list[str]"  # Assume string list for empty
            else:
                type_str = " | ".join(types)
            print(f'    {key}: {type_str}')
    else:
        print("    pass  # No optional fields")

    # Additional analysis
    print(f"\n{'=' * 60}")
    print("ADDITIONAL ANALYSIS")
    print("=" * 60)

    # Check for empty values in always-present keys
    if always_present:
        print("\nChecking for empty values in always-present keys:")
        for key, _, _, _ in always_present:
            empty_count = sum(1 for emoji in emoji_data if not emoji.get(key))
            if empty_count > 0:
                print(f"  {key}: {empty_count} empty values ({(empty_count/total_emojis)*100:.1f}%)")
            else:
                print(f"  {key}: No empty values")


def main() -> None:
    """Main function to run the analysis."""
    try:
        emoji_data = fetch_emoji_data()
        analyze_keys(emoji_data)

        print(f"\n{'=' * 60}")
        print("ANALYSIS COMPLETE")
        print("=" * 60)
        print("Use the TypedDict suggestions above to update your EmojiData structure.")

    except Exception as e:
        print(f"Error: {e}")
        return


if __name__ == "__main__":
    main()
