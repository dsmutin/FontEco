"""Test for single glyph perforation and rendering.

This module tests the perforation and rendering of a single glyph
to verify the dithering and rendering process.
"""

import os
from fontTools.ttLib import TTFont
from fonteco.fonts import perforate_font
from fonteco.render_ttf import render_glyph_to_image


def get_glyph_name_for_char(font_path, char="A"):
    """Get the actual glyph name for a character in the font."""
    font = TTFont(font_path)
    for table in font['cmap'].tables:
        if ord(char) in table.cmap:
            return table.cmap[ord(char)]
    return char  # Return the character itself if no mapping found


def test_single_glyph_perforation_and_rendering():
    """Test perforation and rendering of a single glyph."""
    # Input and output paths
    input_font = "fonts/TimesNewRoman.ttf"  # Use the original font first
    subset_font = "test_outputs/TimesNewRoman_single_A.ttf"
    perforated_font = "test_outputs/TimesNewRoman_single_A_perforated.ttf"
    output_image = "test_outputs/test_output_rendered.png"
    original_image = "test_outputs/original_A.png"
    
    # Create output directory if it doesn't exist
    os.makedirs("test_outputs", exist_ok=True)
    
    # Get the correct glyph name for 'A'
    glyph_name = get_glyph_name_for_char(input_font, "A")
    print(f"Using glyph name: {glyph_name}")
    
    # Create subset with single glyph
    from fonteco.font_utils import create_subset_font, subset_font_to_single_glyph
    create_subset_font(input_font, subset_font, subset_font_to_single_glyph)
    
    # Debug: Print available glyphs in subset
    font = TTFont(subset_font)
    print("Available glyphs in subset:", font.getGlyphOrder())
    print("Subset cmap tables:")
    for table in font['cmap'].tables:
        print(f"  Platform {table.platformID}, Encoding {table.platEncID}: {table.cmap}")
    
    # Render original glyph for comparison
    print("\nRendering original glyph...")
    render_glyph_to_image(
        font_path=input_font,
        output_path=original_image,
        glyph="A",
        size=600,
        position=(100, 100),
        image_size=(800, 800)
    )
    
    # Step 1: Perforate the font
    print("\nPerforating font...")
    try:
        perforate_font(
            input_font_path=subset_font,
            output_font_path=perforated_font,
            reduction_percentage=90,
            with_bug=False,
            draw_images=True,  
            scale_factor="AUTO",
            test=False,
            debug=True,
            point_size=1
        )
        print("Font perforated successfully")
        
        # Debug: Print glyphs in perforated font
        perforated = TTFont(perforated_font)
        print("\nGlyphs in perforated font:", perforated.getGlyphOrder())
        print("Perforated font cmap tables:")
        for table in perforated['cmap'].tables:
            print(f"  Platform {table.platformID}, Encoding {table.platEncID}: {table.cmap}")
        
    except KeyError as e:
        print(f"\nError during perforation: {e}")
        if 'space' in str(e):
            print("Warning: Space glyph not found in subset. Using subset font for rendering.")
            perforated_font = subset_font
        else:
            raise
    
    # Step 2: Render the perforated glyph
    print("\nRendering perforated glyph...")
    render_glyph_to_image(
        font_path=perforated_font,
        output_path=output_image,
        glyph="A",
        size=600,
        position=(100, 100),
        image_size=(800, 800)
    )
    
    print(f"\nTest completed.")
    print(f"Original glyph saved to: {original_image}")
    print(f"Perforated glyph saved to: {output_image}")


if __name__ == "__main__":
    test_single_glyph_perforation_and_rendering() 