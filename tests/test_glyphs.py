import pytest
from PIL import Image, ImageDraw
from fontTools.ttLib import TTFont
from fonteco.glyphs import decompose_glyph, image_to_glyph

@pytest.fixture
def test_font():
    return TTFont("fonts/Times_subset.ttf")

@pytest.fixture
def test_image():
    image = Image.new("L", (512, 512), 255)
    draw = ImageDraw.Draw(image)
    return image, draw

def test_decompose_glyph(test_font):
    glyph_set = test_font.getGlyphSet()
    glyph = test_font["glyf"]["A"]
    
    if glyph.isComposite():
        pen = decompose_glyph(glyph, glyph_set)
        assert pen is not None
        assert hasattr(pen, 'value')
    else:
        pen = decompose_glyph(glyph, glyph_set)
        assert pen is None

def test_image_to_glyph(test_font, test_image):
    image, _ = test_image
    scale_factor = 3.5
    with_bug = False
    
    # Create a simple test image with a black square
    draw = ImageDraw.Draw(image)
    draw.rectangle([100, 100, 200, 200], fill=0)
    
    glyph = image_to_glyph(image, scale_factor, test_font, with_bug)
    
    assert glyph is not None
    assert hasattr(glyph, 'coordinates')
    assert hasattr(glyph, 'endPtsOfContours')
    assert len(glyph.coordinates) > 0 