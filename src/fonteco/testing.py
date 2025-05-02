"""Testing utilities for font perforation.

This module provides functions for testing the font perforation process,
including visualization of the perforation effect on sample glyphs.
"""

from PIL import Image, ImageDraw, ImageFont
from .dithering import generate_sobol_sequence, apply_blue_noise_dithering


def visualize_perforation(input_font_path, output_test_path, reduction_percentage):
    """
    Visualize the perforation process on a sample glyph.
    
    Args:
        input_font_path (str): Path to the input font file
        output_test_path (str): Path to save the test output image
        reduction_percentage (float): Percentage of dots to remove (0-100)
    """
    # Create a temporary image to render the font glyphs
    image_size = (800, 800)  # Size of the image for rendering glyphs
    image = Image.new("L", image_size, 255)  # White background
    draw = ImageDraw.Draw(image)

    # Generate Sobol' sequence points
    num_points = int(image_size[0] * image_size[1] * (reduction_percentage / 100))
    sobol_points = generate_sobol_sequence(image_size[0], image_size[1], num_points)

    # Load the font into PIL for rendering
    pil_font = ImageFont.truetype(input_font_path, size=600)

    # Render the text to get the glyphs
    draw.text((10, 10), "Aa", font=pil_font, fill=0)  # Render a sample glyph

    # Apply blue noise dithering
    perforated_image = apply_blue_noise_dithering(image, sobol_points, point_size=1)
    # Save the perforated image (for visualization)
    perforated_image.save(output_test_path)

    print(f"Perforated font saved to {output_test_path}") 