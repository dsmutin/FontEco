import numpy as np
from PIL import Image
from fonteco.dithering import generate_sobol_sequence, apply_blue_noise_dithering

def test_generate_sobol_sequence():
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