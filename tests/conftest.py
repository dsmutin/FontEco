import pytest
from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw

@pytest.fixture(scope="session")
def times_font():
    return TTFont("fonts/Times_subset.ttf")

@pytest.fixture
def test_image():
    image = Image.new("L", (512, 512), 255)
    draw = ImageDraw.Draw(image)
    return image, draw

@pytest.fixture
def input_font_path():
    return "fonts/Times_subset.ttf"

@pytest.fixture
def output_font_path(tmp_path):
    return str(tmp_path / "Times_perforated_15.ttf")

@pytest.fixture
def output_test_path(tmp_path):
    return str(tmp_path / "test_output.png") 