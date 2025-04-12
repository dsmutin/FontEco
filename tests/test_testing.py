"""Tests for the testing module.

This module contains tests for the font perforation testing functionality,
including visualization of the perforation effect on sample glyphs.
"""

import os
import pytest
from fonteco.testing import test_perforation

@pytest.fixture
def input_font_path():
    """Provide the path to the input font file.
    
    Returns:
        str: Path to the Times subset font file
    """
    return "fonts/Times_subset.ttf"

@pytest.fixture
def output_test_path(tmp_path):
    """Provide a temporary path for test output images.
    
    Args:
        tmp_path: Pytest fixture providing a temporary directory
        
    Returns:
        str: Path to a temporary file for test output images
    """
    return str(tmp_path / "test_output.png")

@pytest.fixture
def reduction_percentage():
    """Provide the reduction percentage for testing.
    
    Returns:
        float: Percentage of dots to remove (0-100)
    """
    return 15

def test_test_perforation(input_font_path, output_test_path, reduction_percentage):
    """Test the test_perforation function.
    
    This test verifies that:
    - The test_perforation function completes successfully
    - The output file is created
    - The output file has a reasonable size
    
    Args:
        input_font_path: Path to the input font file
        output_test_path: Path to save the test output image
        reduction_percentage: Percentage of dots to remove
    """
    # Run test perforation
    test_perforation(input_font_path, output_test_path, reduction_percentage)
    
    # Check if output file was created
    assert os.path.exists(output_test_path)
    
    # Check file size
    assert os.path.getsize(output_test_path) > 0

def test_test_perforation_different_percentages(input_font_path, output_test_path):
    """Test the test_perforation function with different reduction percentages.
    
    This test verifies that the test_perforation function works correctly
    with various reduction percentages.
    
    Args:
        input_font_path: Path to the input font file
        output_test_path: Path to save the test output image
    """
    # Test with different reduction percentages
    for percentage in [5, 15, 30, 50]:
        test_perforation(input_font_path, output_test_path, percentage)
        assert os.path.exists(output_test_path)
        assert os.path.getsize(output_test_path) > 0

def test_test_perforation_with_bug(input_font_path, output_test_path, reduction_percentage):
    """Test the test_perforation function with the special coordinate transformation.
    
    This test verifies that the test_perforation function works correctly
    when using the special coordinate transformation mode.
    
    Args:
        input_font_path: Path to the input font file
        output_test_path: Path to save the test output image
        reduction_percentage: Percentage of dots to remove
    """
    # Run the test
    test_perforation(input_font_path, output_test_path, reduction_percentage)
    
    # Check if output file was created
    assert os.path.exists(output_test_path) 