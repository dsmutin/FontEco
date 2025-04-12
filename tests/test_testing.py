import pytest
import os
from fonteco.testing import test_perforation

@pytest.fixture
def input_font_path():
    return "fonts/Times_subset.ttf"

@pytest.fixture
def output_test_path(tmp_path):
    return str(tmp_path / "test_output.png")

@pytest.fixture
def reduction_percentage():
    return 15

def test_test_perforation(input_font_path, output_test_path, reduction_percentage):
    # Run test perforation
    test_perforation(input_font_path, output_test_path, reduction_percentage)
    
    # Check if output file was created
    assert os.path.exists(output_test_path)
    
    # Check file size
    assert os.path.getsize(output_test_path) > 0

def test_test_perforation_different_percentages(input_font_path, output_test_path):
    # Test with different reduction percentages
    for percentage in [5, 15, 30, 50]:
        test_perforation(input_font_path, output_test_path, percentage)
        assert os.path.exists(output_test_path)
        assert os.path.getsize(output_test_path) > 0 