"""Test for different font rendering modes.

This module tests both original and simplified rendering modes to compare
their effects on font size and quality.
"""

import os
from fontTools.ttLib import TTFont
from fonteco.fonts import perforate_font
from fonteco.render_ttf import render_glyph_to_image
from fonteco.font_utils import create_subset_font, subset_font_to_glyphs


def test_rendering_modes():
    """Test and compare different rendering modes."""
    # Input and output paths
    input_font = "fonts/Times.ttf"
    subset_font = "fonts/test.ttf"
    original_output = "test_outputs/original_mode.ttf"
    simplified_output = "test_outputs/simplified_mode.ttf"
    debug_dir = "test_outputs/debug_glyphs"
    
    # Create output directories
    os.makedirs("test_outputs", exist_ok=True)
    os.makedirs(debug_dir, exist_ok=True)
    
    # Create subset with specified glyphs
    print("Creating font subset...")
    glyphs = ['A', 'a', ' ']  # Test with uppercase and lowercase
    create_subset_font(input_font, subset_font, lambda f: subset_font_to_glyphs(f, glyphs))
    
    # Test original mode
    print("\nTesting original rendering mode...")
    perforate_font(
        input_font_path=subset_font,
        output_font_path=original_output,
        reduction_percentage=90,
        with_bug=False,
        draw_images=True,
        scale_factor="AUTO",
        test=False,
        debug=True,
        point_size=1,
        render_mode="original",
        debug_dir=os.path.join(debug_dir, "original")
    )
    
    # Test simplified mode with different num_levels
    num_levels_to_test = [4, 8]
    for num_levels in num_levels_to_test:
        print(f"\nTesting simplified rendering mode with {num_levels} levels...")
        output_path = f"test_outputs/simplified_mode_{num_levels}.ttf"
        perforate_font(
            input_font_path=subset_font,
            output_font_path=output_path,
            reduction_percentage=90,
            with_bug=False,
            draw_images=True,
            scale_factor="AUTO",
            test=False,
            debug=True,
            point_size=1,
            render_mode="simplified",
            num_levels=num_levels,
            debug_dir=os.path.join(debug_dir, f"simplified_{num_levels}")
        )
        
        # Render comparison image
        render_glyph_to_image(
            font_path=output_path,
            output_path=os.path.join(debug_dir, f"simplified_{num_levels}_rendered.png"),
            glyph="Aa",
            size=600,
            position=(100, 100),
            image_size=(800, 800)
        )
    
    # Compare file sizes
    original_size = os.path.getsize(original_output)
    print("\nResults:")
    print(f"Original mode font size: {original_size / 1024:.2f} KB")
    
    for num_levels in num_levels_to_test:
        output_path = f"test_outputs/simplified_mode_{num_levels}.ttf"
        simplified_size = os.path.getsize(output_path)
        print(f"Simplified mode ({num_levels} levels) font size: {simplified_size / 1024:.2f} KB")
        print(f"Size reduction: {(1 - simplified_size / original_size) * 100:.2f}%")
    
    print(f"\nTest completed. Debug images saved to: {debug_dir}")


if __name__ == "__main__":
    test_rendering_modes() 