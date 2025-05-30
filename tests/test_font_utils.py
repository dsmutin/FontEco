"""Tests for the font utilities module.

This module contains tests for font subsetting and manipulation utilities.
"""

import os
import tempfile

import pytest
from fontTools.ttLib import TTFont

from fonteco.font_utils import subset_font_to_alphanumeric


@pytest.fixture
def test_font():
    """Provide a test font object.
    
    Returns:
        TTFont: A Times font object loaded from the subset font file
    """
    return TTFont("fonts/Times_subset.ttf")


def test_subset_font_to_alphanumeric(test_font):
    """Test the alphanumeric font subsetting functionality.
    
    This test verifies that:
    - The subsetted font contains all alphanumeric characters
    - The subsetted font is not significantly larger than the original
    - The subsetting process handles temporary files correctly
    
    Args:
        test_font: A pytest fixture providing a test font object
    """
    # Create a temporary font file for testing
    with tempfile.NamedTemporaryFile(suffix='.ttf', delete=False) as tmp:
        test_font.save(tmp.name)
        tmp_path = tmp.name
    
    try:
        # Subset the font
        subsetted_font = subset_font_to_alphanumeric(tmp_path)
        
        # Get the character set from the subsetted font
        cmap = subsetted_font.getBestCmap()
        subset_chars = set(cmap.keys())
        
        # Define expected characters
        expected_chars = set()
        for char in range(ord('a'), ord('z') + 1):
            expected_chars.add(char)
        for char in range(ord('A'), ord('Z') + 1):
            expected_chars.add(char)
        for char in range(ord('0'), ord('9') + 1):
            expected_chars.add(char)
        
        # Check that all expected characters are present
        assert expected_chars.issubset(subset_chars), (
            "Not all alphanumeric characters are present in the subsetted font"
        )
        
        # Check that the font is not significantly larger than the original
        original_size = os.path.getsize(tmp_path)
        with tempfile.NamedTemporaryFile(suffix='.ttf', delete=False) as tmp_subset:
            subsetted_font.save(tmp_subset.name)
            subset_size = os.path.getsize(tmp_subset.name)
            # Allow for some overhead in the subsetted font
            assert subset_size <= original_size * 1.1, (
                f"Subsetted font is significantly larger than original "
                f"(original: {original_size}, subset: {subset_size})"
            )
            os.unlink(tmp_subset.name)
            
    finally:
        # Clean up
        os.unlink(tmp_path) 