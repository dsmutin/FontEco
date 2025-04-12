from src.fonteco.fonts import perforate_font
from src.fonteco.testing import test_perforation

input_font_path = "fonts/TimesNewRoman_subset.ttf"
reduction_percentage = 40
output_font_path = "fonts/EcoTimesNewRoman_"+str(reduction_percentage)+".ttf"

#run test
test_perforation(
    input_font_path,
    "fonts/test_output.png",
    reduction_percentage)

#perforate font
perforate_font(
    input_font_path=input_font_path,
    output_font_path=output_font_path,
    reduction_percentage=reduction_percentage,
    debug=True
    )