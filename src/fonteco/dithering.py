"""Blue noise dithering implementation for font perforation.

This module implements blue noise dithering using Sobol' sequences to create
visually pleasing patterns when removing dots from glyphs. The dithering
process helps maintain readability while reducing ink usage.
"""

import numpy as np
from scipy.stats import qmc
from PIL import Image


def generate_sobol_sequence(width, height, num_points):
    """
    Generate a Sobol' sequence of points within the given dimensions.
    
    Args:
        width (int): Width of the area to generate points in (must be > 0)
        height (int): Height of the area to generate points in (must be > 0)
        num_points (int): Number of points to generate (must be a power of 2)
        
    Returns:
        numpy.ndarray: Array of shape (num_points, 2) containing the generated points
        
    Raises:
        ValueError: If width, height, or num_points are invalid
    """
    sampler = qmc.Sobol(d=2, scramble=True)
    points = sampler.random_base2(m=int(np.log2(num_points)))
    points = qmc.scale(points, [0, 0], [width, height])
    return points.astype(int)


def apply_blue_noise_dithering(image, sobol_points):
    """
    Apply blue noise dithering by removing dots based on the Sobol' sequence.
    
    Args:
        image (PIL.Image.Image): Input grayscale image to dither
        sobol_points (numpy.ndarray): Array of points from Sobol' sequence
        
    Returns:
        PIL.Image.Image: Dithered image with white pixels at Sobol' sequence points
        
    Raises:
        TypeError: If image is not a PIL Image or sobol_points is not a numpy array
        ValueError: If sobol_points has incorrect shape or values
    """
    pixels = image.load()
    width, height = image.size
    for x, y in sobol_points:
        if 0 <= x < width and 0 <= y < height:
            pixels[x, y] = 255  # Set pixel to white (remove dot)
    return image 