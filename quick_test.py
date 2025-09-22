#!/usr/bin/env python3
"""
Quick test of the emoji generator functionality
"""

import tempfile
from pathlib import Path
import sys
import os

# Add current directory to path
sys.path.insert(0, os.getcwd())

try:
    # Import and test the main functionality
    from emoji_alfred_generator import EmojiSnippetGenerator

    print("✓ Successfully imported EmojiSnippetGenerator")

    # Test basic functionality
    generator = EmojiSnippetGenerator(prefix=";")
    print("✓ Created generator instance")

    # Test Unicode conversion
    emoji_char = generator.unicode_to_emoji("1F600")
    if emoji_char == "😀":
        print("✓ Unicode to emoji conversion works")
    else:
        print("✗ Unicode conversion failed")
        sys.exit(1)

    # Test snippet creation
    snippet = generator.create_snippet("😀", "grinning", "Grinning Face")
    if snippet["alfredsnippet"]["keyword"] == ";grinning":
        print("✓ Snippet creation works")
    else:
        print("✗ Snippet creation failed")
        sys.exit(1)

    # Test with limited emojis (don't fetch full dataset)
    print("✓ Basic functionality test passed!")
    print("\nTo run the full generator:")
    print("  python emoji_alfred_generator.py --max-emojis 10 -o test.alfredsnippets")

except ImportError as e:
    raise
    print(f"✗ Import failed: {e}")
    sys.exit(1)
except Exception as e:
    raise
    print(f"✗ Test failed: {e}")
    sys.exit(1)
