"""Testing utilities for font perforation.

This module provides functions for testing the font perforation process,
including visualization of the perforation effect on sample glyphs.
"""

from PIL import Image, ImageDraw, ImageFont
from fontTools.ttLib import TTFont
from .dithering import generate_sobol_sequence, apply_blue_noise_dithering, apply_shape_dithering
from .fonts import perforate_font
from .font_utils import create_subset_font, subset_font_to_glyphs


def test_perforation_rendering(input_font_path, output_test_path, reduction_percentage=20):
    """
    Test the perforation process on a single glyph and render the result.
    
    Args:
        input_font_path (str): Path to the input font file
        output_test_path (str): Path to save the test output image
        reduction_percentage (float): Percentage of dots to remove (0-100)
    """
    # Create temporary paths
    import os
    import tempfile
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create paths for temporary files
        subset_path = os.path.join(temp_dir, "subset.ttf")
        perforated_path = os.path.join(temp_dir, "perforated.ttf")
        
        # Create subset with single glyph
        print("Creating single glyph subset...")
        create_subset_font(input_font_path, subset_path, subset_font_to_glyphs)
        
        # Perforate the subset
        print("Perforating font...")
        perforate_font(
            input_font_path=subset_path,
            output_font_path=perforated_path,
            reduction_percentage=reduction_percentage,
            with_bug=False,
            draw_images=False,
            scale_factor="AUTO",
            test=False,
            debug=True
        )
        
        # Render the result
        print("Rendering result...")
        # Create a white background image
        image_size = (800, 800)
        image = Image.new("L", image_size, 255)
        draw = ImageDraw.Draw(image)
        
        # Load the perforated font
        font = ImageFont.truetype(perforated_path, size=600)
        
        # Draw the glyph
        draw.text((100, 100), "A", font=font, fill=0)
        
        # Save the result
        image.save(output_test_path)
        print(f"Test result saved to {output_test_path}")


def visualize_perforation(
    input_font_path,
    output_test_path,
    reduction_percentage,
    dithering_mode="blue_noise",
    shape_type="circle",
    shape_size=10,
    margin=1,
    num_levels=4
):
    """
    Visualize the perforation process on a sample glyph.
    
    Args:
        input_font_path (str): Path to the input font file
        output_test_path (str): Path to save the test output image
        reduction_percentage (float): Percentage of dots to remove (0-100)
        dithering_mode (str): Dithering mode to use:
            - "original": Uses blue noise dithering with Sobol' sequence
            - "shape": Uses shape-based dithering with circles or rectangles
        shape_type (str): Type of shape to use for shape dithering ("circle" or "rectangle")
        shape_size (int or str): Size of shapes for shape dithering:
            - int: exact size
            - "random": random size between margin*2 and max possible
            - "biggest": biggest possible size that fits
        margin (int): Minimum margin between shapes and edges for shape dithering
        num_levels (int): Number of transparency levels for simplified mode
    """
    # Create a temporary image to render the font glyphs
    image_size = (800, 800)  # Size of the image for rendering glyphs
    image = Image.new("L", image_size, 255)  # White background
    draw = ImageDraw.Draw(image)

    # Load the font into PIL for rendering
    pil_font = ImageFont.truetype(input_font_path, size=600)

    # Render the text to get the glyphs
    draw.text((10, 10), "Aa", font=pil_font, fill=0)  # Render a sample glyph

    # Apply dithering based on render mode
    if dithering_mode == "shape":
        perforated_image = apply_shape_dithering(
            image,
            shape_type=shape_type,
            margin=margin,
            shape_size=shape_size,
            reduction_percentage=reduction_percentage
        )
    else:
        # Generate Sobol' sequence points
        num_points = int(image_size[0] * image_size[1] * (reduction_percentage / 100))
        sobol_points = generate_sobol_sequence(image_size[0], image_size[1], num_points)
        perforated_image = apply_blue_noise_dithering(image, sobol_points)

    # Save the perforated image (for visualization)
    perforated_image.save(output_test_path)
    print(f"Perforated font saved to {output_test_path}") 