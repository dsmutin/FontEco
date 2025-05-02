"""Main pipeline for font perforation process.

This script orchestrates the font perforation process by:
1. Testing the perforation on a sample
2. Applying the perforation to create a new font file
"""

from src.fonteco.fonts import perforate_font
from src.fonteco.testing import visualize_perforation


INPUT_FONT_PATH = "fonts/Times_subset.ttf"
REDUCTION_PERCENTAGE = 50
OUTPUT_FONT_PATH = f"test_outputs/EcoTimes_{REDUCTION_PERCENTAGE}.ttf"


def main():
    """Run the font perforation pipeline."""
    # Run test
    visualize_perforation(
        INPUT_FONT_PATH,
        "test_outputs/test_output.png",
        REDUCTION_PERCENTAGE
    )

    # Perforate font
    perforate_font(
        input_font_path=INPUT_FONT_PATH,
        output_font_path=OUTPUT_FONT_PATH,
        reduction_percentage=REDUCTION_PERCENTAGE
    )


if __name__ == "__main__":
    main()