"""Font rendering utilities.

This module provides functions for rendering TTF fonts to images.
"""

from PIL import Image, ImageDraw, ImageFont
from fontTools.ttLib import TTFont


def get_glyph_name_for_char(font_path, char):
    """Get the actual glyph name for a character in the font."""
    font = TTFont(font_path)
    for table in font['cmap'].tables:
        if ord(char) in table.cmap:
            return table.cmap[ord(char)]
    return char  # Return the character itself if no mapping found


def render_glyph_to_image(font_path, output_path, glyph="A", size=600, position=(100, 100), image_size=(800, 800)):
    """
    Render a single glyph from a TTF font to an image.
    
    Args:
        font_path (str): Path to the TTF font file
        output_path (str): Path to save the output image
        glyph (str): The glyph to render (default: "A")
        size (int): Font size in pixels (default: 600)
        position (tuple): (x, y) position to render the glyph (default: (100, 100))
        image_size (tuple): Size of the output image (default: (800, 800))
    """
    # Create a white background image
    image = Image.new("L", image_size, 255)
    draw = ImageDraw.Draw(image)
    
    try:
        # Debug: Check font file
        print(f"\nRendering from font: {font_path}")
        font_check = TTFont(font_path)
        print("Available glyphs:", font_check.getGlyphOrder())
        print("cmap tables:")
        for table in font_check['cmap'].tables:
            print(f"  Platform {table.platformID}, Encoding {table.platEncID}: {table.cmap}")
        
        # Load the font for rendering
        try:
            font = ImageFont.truetype(font_path, size=size)
            print(f"Font loaded successfully with size {size}")
        except Exception as e:
            print(f"Error loading font: {e}")
            raise
        
        # Get the actual glyph name if needed
        if len(glyph) == 1:  # If it's a character, get its glyph name
            glyph_name = get_glyph_name_for_char(font_path, glyph)
            print(f"Rendering glyph '{glyph}' with name '{glyph_name}'")
        
        # Draw the glyph
        bbox = draw.textbbox(position, glyph, font=font)
        print(f"Text bounding box: {bbox}")
        draw.text(position, glyph, font=font, fill=0)
        
        # Check if anything was drawn
        bbox_width = bbox[2] - bbox[0]
        bbox_height = bbox[3] - bbox[1]
        if bbox_width <= 0 or bbox_height <= 0:
            print("Warning: No glyph was drawn (empty bounding box)")
        else:
            print(f"Glyph drawn with size: {bbox_width}x{bbox_height}")
        
        # Save the result
        image.save(output_path)
        
        # Debug: Check the saved image
        saved_image = Image.open(output_path)
        print(f"Image saved with size {saved_image.size}, mode {saved_image.mode}")
        extrema = saved_image.getextrema()
        print(f"Image value range: {extrema}")
        
    except Exception as e:
        print(f"Error rendering glyph: {e}")
        # Save empty image as fallback
        image.save(output_path) 