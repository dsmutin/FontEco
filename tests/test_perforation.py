"""Tests for the font perforation functionality."""

import os
import pytest
from PIL import Image
from fonteco.testing import visualize_perforation
from fonteco.dithering import generate_sobol_sequence, apply_blue_noise_dithering


@pytest.fixture
def sample_font_path(tmp_path):
    """Create a temporary font file for testing."""
    # For testing purposes, we'll use a system font
    # You might want to replace this with a test font file
    return "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


@pytest.fixture
def output_path(tmp_path):
    """Create a temporary output path for test results."""
    return str(tmp_path / "test_output.png")


def test_visualize_perforation(sample_font_path, output_path):
    """Test the visualization of perforation process."""
    reduction_percentage = 30
    
    # Run the visualization
    visualize_perforation(sample_font_path, output_path, reduction_percentage)
    
    # Verify the output file exists
    assert os.path.exists(output_path)
    
    # Verify the output is a valid image
    with Image.open(output_path) as img:
        assert img.mode == "L"  # Should be grayscale
        assert img.size == (800, 800)  # Should match the expected size


def test_sobol_sequence_generation():
    """Test the Sobol sequence generation."""
    width, height = 100, 100
    num_points = 64  # Power of 2
    
    points = generate_sobol_sequence(width, height, num_points)
    
    assert points.shape == (num_points, 2)
    assert points.dtype == int
    assert (points >= 0).all()
    assert (points[:, 0] < width).all()
    assert (points[:, 1] < height).all()


def test_blue_noise_dithering():
    """Test the blue noise dithering application."""
    # Create a test image
    image = Image.new("L", (100, 100), 0)  # Black image
    num_points = 64
    points = generate_sobol_sequence(100, 100, num_points)
    
    # Apply dithering
    result = apply_blue_noise_dithering(image, points, point_size=1)
    
    assert isinstance(result, Image.Image)
    assert result.size == (100, 100)
    assert result.mode == "L" 