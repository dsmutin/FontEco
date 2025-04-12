"""Main pipeline for font perforation process.

This script orchestrates the font perforation process by:
1. Testing the perforation on a sample
2. Applying the perforation to create a new font file
"""

from src.fonteco.fonts import perforate_font
from src.fonteco.testing import test_perforation


INPUT_FONT_PATH = "fonts/TimesNewRoman_subset.ttf"
REDUCTION_PERCENTAGE = 40
OUTPUT_FONT_PATH = f"fonts/EcoTimesNewRoman_{REDUCTION_PERCENTAGE}.ttf"


def main():
    """Run the font perforation pipeline."""
    # Run test
    test_perforation(
        INPUT_FONT_PATH,
        "fonts/test_output.png",
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