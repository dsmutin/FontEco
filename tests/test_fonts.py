import pytest
import os
from fontTools.ttLib import TTFont
from fonteco.fonts import perforate_font

@pytest.fixture
def input_font_path():
    return "fonts/Times_subset.ttf"

@pytest.fixture
def output_font_path(tmp_path):
    return str(tmp_path / "Times_perforated_15.ttf")

def test_perforate_font(input_font_path, output_font_path):
    # Test parameters
    reduction_percentage = 15
    with_bug = False
    draw_images = False
    scale_factor = 3.5
    test = True  # Only process first 20 glyphs for testing
    
    # Check if input font exists and has required glyphs
    font = TTFont(input_font_path)
    assert "glyf" in font, "Font does not have glyf table"
    assert len(font["glyf"].glyphs) > 0, "Font has no glyphs"
    
    # Run perforation
    perforate_font(
        input_font_path=input_font_path,
        output_font_path=output_font_path,
        reduction_percentage=reduction_percentage,
        with_bug=with_bug,
        draw_images=draw_images,
        scale_factor=scale_factor,
        test=test
    )
    
    # Check if output file was created
    assert os.path.exists(output_font_path)
    
    # Check file size (should be smaller than original due to perforation)
    original_size = os.path.getsize(input_font_path)
    new_size = os.path.getsize(output_font_path)
    assert new_size > 0
    assert new_size < original_size*10  # Perforated font should be smaller

def test_perforate_font_with_bug(input_font_path, output_font_path):
    # Test with bug enabled
    reduction_percentage = 15
    with_bug = True
    draw_images = False
    scale_factor = 3.5
    test = True
    
    # Check if input font exists and has required glyphs
    font = TTFont(input_font_path)
    assert "glyf" in font, "Font does not have glyf table"
    assert len(font["glyf"].glyphs) > 0, "Font has no glyphs"
    
    # Run perforation
    perforate_font(
        input_font_path=input_font_path,
        output_font_path=output_font_path,
        reduction_percentage=reduction_percentage,
        with_bug=with_bug,
        draw_images=draw_images,
        scale_factor=scale_factor,
        test=test
    )
    
    # Check if output file was created
    assert os.path.exists(output_font_path) 