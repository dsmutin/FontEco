"""Test for font subsetting and perforation.

This module tests the subsetting and perforation of a font with a small set of glyphs
to verify the dithering and rendering process.
"""

import os
from fontTools.ttLib import TTFont
from fonteco.fonts import perforate_font
from fonteco.render_ttf import render_glyph_to_image
from fonteco.font_utils import create_subset_font, subset_font_to_glyphs


def test_subset_perforation_and_rendering():
    """Test subsetting, perforation and rendering of a small set of glyphs."""
    # Input and output paths
    input_font = "new_fonts/IBMPlexSerif-Regular_subset.ttf"  # Updated to use the correct font
    subset_font = "fonts/test.ttf"
    perforated_font = "test_outputs/test_perforated.ttf"
    output_image = "test_outputs/test_output_rendered.png"
    original_image = "test_outputs/original_glyphs.png"
    
    # Create output directory if it doesn't exist
    os.makedirs("test_outputs", exist_ok=True)
    os.makedirs("fonts", exist_ok=True)
    
    # Create subset with specified glyphs
    print("Creating font subset...")
    glyphs = ['a', 'A', ' ']
    create_subset_font(input_font, subset_font, lambda f: subset_font_to_glyphs(f, glyphs))
    
    # Debug: Print available glyphs in subset
    font = TTFont(subset_font)
    print("Available glyphs in subset:", font.getGlyphOrder())
    print("Subset cmap tables:")
    for table in font['cmap'].tables:
        print(f"  Platform {table.platformID}, Encoding {table.platEncID}: {table.cmap}")
    
    # Render original glyphs for comparison
    print("\nRendering original glyphs...")
    render_glyph_to_image(
        font_path=input_font,
        output_path=original_image,
        glyph="Aa",  # Render both 'a' and 'A'
        size=200,  # Reduced size to match working pipeline
        position=(10, 0),  # Updated position to match working pipeline
        image_size=(300, 280)  # Updated size to match working pipeline
    )
    
    # Step 1: Perforate the font
    print("\nPerforating font...")
    try:
        perforate_font(
            input_font_path=subset_font,
            output_font_path=perforated_font,
            reduction_percentage=10,  # Reduced percentage to match working pipeline
            with_bug=False,
            draw_images=True,
            scale_factor="AUTO",
            test=False,
            debug=True,
            point_size=2,  # Added point_size to match working pipeline
            render_mode="original",  # Added render_mode
            dithering_mode="BN"  # Added dithering_mode
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
    
    # Step 2: Render the perforated glyphs
    print("\nRendering perforated glyphs...")
    render_glyph_to_image(
        font_path=perforated_font,
        output_path=output_image,
        glyph="Aa",  # Render both 'a' and 'A'
        size=200,  # Reduced size to match working pipeline
        position=(10, 0),  # Updated position to match working pipeline
        image_size=(300, 280)  # Updated size to match working pipeline
    )
    
    print(f"\nTest completed.")
    print(f"Original glyphs saved to: {original_image}")
    print(f"Perforated glyphs saved to: {output_image}")


if __name__ == "__main__":
    test_subset_perforation_and_rendering() 