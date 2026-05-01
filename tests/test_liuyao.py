#!/usr/bin/env python3
"""Tests for liuyao-skill."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from liuyao_interactive import get_yao_type
from hexagrams import HEXAGRAMS
from naga import HEX

def test_get_yao_type():
    """Test yao determination logic."""
    assert get_yao_type(("🌕", "🌕", "🌕")) == ("老阳", "⚊", True)
    assert get_yao_type(("🌑", "🌑", "🌑")) == ("老阴", "⚋", True)
    assert get_yao_type(("🌕", "🌕", "🌑")) == ("少阳", "⚊", False)
    assert get_yao_type(("🌑", "🌑", "🌕")) == ("少阴", "⚋", False)
    print("✓ get_yao_type tests passed")

def test_hexagrams_database():
    """Test 64 hexagrams database completeness."""
    assert len(HEXAGRAMS) == 64
    print(f"✓ All {len(HEXAGRAMS)} hexagrams loaded")

def test_hex_lookup():
    """Test hexagram lookup."""
    result = HEX.get(("乾", "乾"))
    assert result is not None
    print("✓ Hex lookup test passed")

if __name__ == "__main__":
    test_get_yao_type()
    test_hexagrams_database()
    test_hex_lookup()
    print("\nAll tests passed!")
