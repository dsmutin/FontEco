"""Script to create a subset of a font containing only alphanumeric characters.

This script takes an input font file and creates a subset containing only
alphanumeric characters, which is useful for reducing font file size while
maintaining support for English text.
"""

from fonteco.font_utils import create_subset_font, subset_font_to_alphanumeric


def main():
    """Create a subset of Times font with alphanumeric characters.
    
    The script processes the input font file and creates a new font file containing
    only the specified character subset.
    """
    input_font = "fonts/Times.ttf"
    output_font = "fonts/Times_subset.ttf"  # Overwrite the existing file
    
    print(f"Re-subsetting {input_font}...")
    create_subset_font(input_font, output_font, subset_font_to_alphanumeric)
    print("Done!")


if __name__ == "__main__":
    main() 