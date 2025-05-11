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


def apply_blue_noise_dithering(image, sobol_points, point_size=1):
    """
    Apply blue noise dithering by removing dots based on the Sobol' sequence.
    
    Args:
        image (PIL.Image.Image): Input grayscale image to dither
        sobol_points (numpy.ndarray): Array of points from Sobol' sequence
        point_size (int): Size of each point to remove (default: 1)
        
    Returns:
        PIL.Image.Image: Dithered image with white pixels at Sobol' sequence points
        
    Raises:
        TypeError: If image is not a PIL Image or sobol_points is not a numpy array
        ValueError: If sobol_points has incorrect shape or values
    """
    pixels = image.load()
    width, height = image.size
    half_size = point_size // 2
    
    for point_x, point_y in sobol_points:
        for dx in range(-half_size, half_size + 1):
            for dy in range(-half_size, half_size + 1):
                x = point_x + dx
                y = point_y + dy
                if 0 <= x < width and 0 <= y < height:
                    pixels[x, y] = 255  # Set pixel to white (remove dot)
    return image 


def simplify_image(image, num_levels=4, debug=False):
    """
    Simplify an image by reducing the number of transparency levels.
    
    Args:
        image (PIL.Image.Image): Input grayscale image to simplify
        num_levels (int): Number of transparency levels to use (2-256)
        debug (bool): If True, print debug information about the simplification process
        
    Returns:
        PIL.Image.Image: Simplified image with reduced transparency levels
        
    Raises:
        ValueError: If num_levels is not between 2 and 256
    """
    if not 2 <= num_levels <= 256:
        raise ValueError("num_levels must be between 2 and 256")
        
    # Convert image to numpy array
    img_array = np.array(image)
    
    if debug:
        print(f"\nImage simplification debug:")
        print(f"Input image shape: {img_array.shape}")
        print(f"Input image min/max values: {img_array.min()}/{img_array.max()}")
        print(f"Number of unique values: {len(np.unique(img_array))}")
    
    # Calculate the step size for each level
    step = 256 // (num_levels - 1)
    
    # Create the new levels
    levels = np.arange(0, 256, step)
    if len(levels) > num_levels:
        levels = levels[:num_levels]
    
    if debug:
        print(f"Step size: {step}")
        print(f"Levels: {levels}")
    
    # Quantize the image
    quantized = np.digitize(img_array, levels) - 1
    simplified = levels[quantized]
    
    if debug:
        print(f"Output image min/max values: {simplified.min()}/{simplified.max()}")
        print(f"Number of unique values in output: {len(np.unique(simplified))}")
    
    return Image.fromarray(simplified.astype(np.uint8)) 


def _get_random_shape_size(min_size, max_size):
    """Helper function to get a random shape size within bounds."""
    raise Warning("This function is under development")
    return np.random.randint(min_size, max_size + 1)

def _get_biggest_possible_shape(image, x, y, margin, shape_type):
    """Helper function to find the biggest possible shape size at given position."""
    raise Warning("This function is under development")
    width, height = image.size
    pixels = image.load()
    
    # Start with maximum possible size
    max_size = min(width, height)
    
    # Check each possible size from max down to minimum
    for size in range(max_size, margin * 2, -1):
        half_size = size // 2
        
        # Check if shape fits within image bounds with margin
        if not (x - half_size >= margin and x + half_size < width - margin and
                y - half_size >= margin and y + half_size < height - margin):
            continue
            
        # Check if shape overlaps with any white pixels (glyph boundaries)
        fits = True
        if shape_type == "circle":
            for dx in range(-half_size, half_size + 1):
                for dy in range(-half_size, half_size + 1):
                    if dx*dx + dy*dy <= half_size*half_size:
                        if pixels[x + dx, y + dy] == 255:
                            fits = False
                            break
                if not fits:
                    break
        else:  # rectangle
            for dx in range(-half_size, half_size + 1):
                for dy in range(-half_size, half_size + 1):
                    if pixels[x + dx, y + dy] == 255:
                        fits = False
                        break
                if not fits:
                    break
                    
        if fits:
            return size
            
    return margin * 2  # Return minimum size if no bigger shape fits

def apply_shape_dithering(image, shape_type="circle", margin=1, shape_size=10, reduction_percentage=20):
    """
    Apply shape-based dithering to an image.
    
    Args:
        image (PIL.Image.Image): Input grayscale image to dither
        shape_type (str): Type of shape to use ("circle" or "rectangle")
        margin (int): Minimum margin between shapes and edges, and between shapes
        shape_size (int or str): Size of shapes. Can be:
            - int: exact size
            - "random": random size between margin*2 and max possible
            - "biggest": biggest possible size that fits
        reduction_percentage (float): Percentage of black pixels to remove (0-100)
            
    Returns:
        PIL.Image.Image: Dithered image with white shapes
        
    Raises:
        ValueError: If shape_type or shape_size is invalid
    """
    if shape_type not in ["circle", "rectangle"]:
        raise ValueError("shape_type must be 'circle' or 'rectangle'")
        
    if not isinstance(shape_size, (int, str)) or (
        isinstance(shape_size, str) and shape_size not in ["random", "biggest"]
    ):
        raise ValueError("shape_size must be an int, 'random', or 'biggest'")
    
    # Convert image to numpy array for easier manipulation
    img_array = np.array(image)
    width, height = image.size
    
    # Create a copy of the image to modify
    result = image.copy()
    pixels = result.load()
    
    # Find all black pixels (potential shape centers)
    black_pixels = np.where(img_array == 0)
    black_pixels = list(zip(black_pixels[1], black_pixels[0]))  # (x, y) format
    
    # Calculate number of shapes to place based on reduction percentage
    num_shapes = int(len(black_pixels) * (reduction_percentage / 100))
    
    # Shuffle black pixels to randomize shape placement
    np.random.shuffle(black_pixels)
    
    # Keep track of placed shapes (center points and sizes)
    placed_shapes = []
    
    for x, y in black_pixels[:num_shapes]:
        # Skip if pixel is already white
        if pixels[x, y] == 255:
            continue
            
        # Determine shape size
        if isinstance(shape_size, int):
            size = shape_size
        elif shape_size == "random":
            # Get maximum possible size first
            max_size = _get_biggest_possible_shape(result, x, y, margin, shape_type)
            # Then get random size between minimum and maximum
            size = _get_random_shape_size(margin * 2, max_size)
        else:  # biggest
            size = _get_biggest_possible_shape(result, x, y, margin, shape_type)
            
        half_size = size // 2
        
        # Check if shape fits within image bounds with margin
        if not (x - half_size >= margin and x + half_size < width - margin and
                y - half_size >= margin and y + half_size < height - margin):
            continue
            
        # Check if shape overlaps with any existing shapes
        overlaps = False
        for center_x, center_y, shape_size in placed_shapes:
            # Calculate distance between shape centers
            distance = ((x - center_x) ** 2 + (y - center_y) ** 2) ** 0.5
            # Shapes should be at least margin + half_size + other_shape_half_size apart
            min_distance = margin + half_size + shape_size // 2
            if distance < min_distance:
                overlaps = True
                break
                    
        if overlaps:
            continue
            
        # Check if shape overlaps with any white pixels (glyph boundaries)
        overlaps = False
        if shape_type == "circle":
            for dx in range(-half_size, half_size + 1):
                for dy in range(-half_size, half_size + 1):
                    if dx*dx + dy*dy <= half_size*half_size:
                        if pixels[x + dx, y + dy] == 255:
                            overlaps = True
                            break
                if overlaps:
                    break
        else:  # rectangle
            for dx in range(-half_size, half_size + 1):
                for dy in range(-half_size, half_size + 1):
                    if pixels[x + dx, y + dy] == 255:
                        overlaps = True
                        break
                if overlaps:
                    break
                    
        if overlaps:
            continue
            
        # Draw the shape
        if shape_type == "circle":
            for dx in range(-half_size, half_size + 1):
                for dy in range(-half_size, half_size + 1):
                    if dx*dx + dy*dy <= half_size*half_size:
                        pixels[x + dx, y + dy] = 255
        else:  # rectangle
            for dx in range(-half_size, half_size + 1):
                for dy in range(-half_size, half_size + 1):
                    pixels[x + dx, y + dy] = 255
                    
        # Record the placed shape
        placed_shapes.append((x, y, size))
                    
    return result