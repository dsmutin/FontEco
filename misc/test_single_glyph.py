"""Script to test the single glyph subsetting functionality.

This script creates a subset of a font containing only the 'A' glyph
and saves it to a new file.
"""

from fonteco.font_utils import create_subset_font, subset_font_to_single_glyph


def main():
    """Create a subset of Times New Roman font with only the 'A' glyph."""
    input_font = "fonts/TimesNewRoman.ttf"
    output_font = "fonts/TimesNewRoman_single_A.ttf"
    
    print(f"Creating subset with only 'A' glyph from {input_font}...")
    create_subset_font(input_font, output_font, subset_font_to_single_glyph)
    print(f"Subset font saved to {output_font}")


if __name__ == "__main__":
    main() 