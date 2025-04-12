"""Pytest configuration and fixtures for font perforation tests.

This module provides common fixtures and configuration for testing the
font perforation functionality.
"""

import pytest
from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw

@pytest.fixture(scope="session")
def times_font():
    """Provide a Times font object for testing.
    
    Returns:
        TTFont: A Times font object loaded from the subset font file
    """
    return TTFont("fonts/Times_subset.ttf")

@pytest.fixture
def test_image():
    """Create a test image and drawing context.
    
    Returns:
        tuple: A tuple containing (image, draw) where image is a PIL Image
              and draw is an ImageDraw context
    """
    image = Image.new("L", (512, 512), 255)
    draw = ImageDraw.Draw(image)
    return image, draw

@pytest.fixture
def input_font_path():
    """Provide the path to the input font file.
    
    Returns:
        str: Path to the Times subset font file
    """
    return "fonts/Times_subset.ttf"

@pytest.fixture
def output_font_path(tmp_path):
    """Provide a temporary path for the output font file.
    
    Args:
        tmp_path: Pytest fixture providing a temporary directory
        
    Returns:
        str: Path to a temporary file for the perforated font
    """
    return str(tmp_path / "Times_perforated_15.ttf")

@pytest.fixture
def output_test_path(tmp_path):
    """Provide a temporary path for test output images.
    
    Args:
        tmp_path: Pytest fixture providing a temporary directory
        
    Returns:
        str: Path to a temporary file for test output images
    """
    return str(tmp_path / "test_output.png") 