from src.fonteco.fonts import perforate_font
from src.fonteco.testing import test_perforation

def main():
    # Example usage
    input_font_path = "fonts/Times_subset.ttf"
    output_font_path = "fonts/EcoTimes_15.ttf"
    reduction_percentage = 15
    with_bug = False
    draw_images = True
    scale_factor = "AUTO"
    test = False

    # Test perforation on a single glyph
    test_perforation(input_font_path, "test_output.png", reduction_percentage)

    # Perforate the entire font
    perforate_font(
        input_font_path=input_font_path,
        output_font_path=output_font_path,
        reduction_percentage=reduction_percentage,
        with_bug=with_bug,
        draw_images=draw_images,
        scale_factor=scale_factor,
        test=test
    )

if __name__ == "__main__":
    main() 