"""Test for all font rendering modes.

This module tests and compares original, simplified, and optimized rendering modes
to evaluate their effects on font size and quality.
"""

import os
import pytest
from fontTools.ttLib import TTFont
from fonteco.fonts import perforate_font
from fonteco.render_ttf import render_glyph_to_image
from fonteco.font_utils import create_subset_font, subset_font_to_glyphs


# Test configurations
test_configs = [
    {
        "name": "original",
        "render_mode": "original",
        "dithering_mode": "blue_noise",
        "num_levels": None,
        "output": "test_outputs/original_mode.ttf"
    },
    {
        "name": "simplified_optimal",
        "render_mode": "simplified",
        "dithering_mode": "blue_noise",
        "num_levels": 4,  # Optimal value for simplified mode
        "output": "test_outputs/simplified_mode_optimal.ttf"
    },
    {
        "name": "optimized_optimal",
        "render_mode": "optimized",
        "dithering_mode": "blue_noise",
        "num_levels": 100,  # Optimal value for optimized mode
        "output": "test_outputs/optimized_mode_optimal.ttf"
    },
    {
        "name": "optimized_masked",
        "render_mode": "optimized_masked",
        "dithering_mode": "blue_noise",
        "num_levels": 100,  # Using same grid size as optimal optimized mode
        "output": "test_outputs/optimized_mode_masked.ttf"
    },
    {
        "name": "shape_circle",
        "render_mode": "original",
        "num_levels": None,
        "dithering_mode": "shape",
        "shape_type": "circle",
        "shape_size": 10,
        "margin": 5,
        "output": "test_outputs/shape_mode_circle.ttf"
    },
    {
        "name": "shape_rectangle",
        "render_mode": "original",
        "num_levels": None,
        "dithering_mode": "shape",
        "shape_type": "rectangle",
        #"shape_size": "biggest",
        "shape_size": 20,
        "margin": 5,
        "output": "test_outputs/shape_mode_rectangle.ttf"
    }
]

# Input and output paths
INPUT_FONT = "fonts/Times.ttf"
SUBSET_FONT = "fonts/test.ttf"
DEBUG_DIR = "test_outputs/debug_all_modes"
TEST_GLYPHS = ['A', 'a', 'B', 'b', ' ']


@pytest.fixture(scope="session")
def setup_test_environment():
    """Create necessary directories and subset font for testing."""
    # Create output directories
    os.makedirs("test_outputs", exist_ok=True)
    os.makedirs(DEBUG_DIR, exist_ok=True)
    
    # Create subset with specified glyphs
    create_subset_font(INPUT_FONT, SUBSET_FONT, lambda f: subset_font_to_glyphs(f, TEST_GLYPHS))
    
    yield
    
    # Cleanup (optional)
    # os.remove(SUBSET_FONT)


@pytest.fixture(params=test_configs)
def config(request):
    """Fixture to provide each test configuration."""
    return request.param


def test_rendering_mode(config, setup_test_environment):
    """Test individual rendering mode configuration."""
    # Create debug directory for this specific test
    test_debug_dir = os.path.join(DEBUG_DIR, config['name'])
    os.makedirs(test_debug_dir, exist_ok=True)
    
    # Run perforation
    perforate_font(
        input_font_path=SUBSET_FONT,
        output_font_path=config['output'],
        reduction_percentage=90,
        with_bug=False,
        draw_images=True,
        scale_factor="AUTO",
        test=False,
        debug=True,
        point_size=1,
        render_mode=config['render_mode'],
        dithering_mode=config['dithering_mode'],
        num_levels=config.get('num_levels'),
        debug_dir=test_debug_dir,
        shape_type=config.get('shape_type'),
        shape_size=config.get('shape_size'),
        margin=config.get('margin')
    )
    
    # Render comparison image
    render_glyph_to_image(
        font_path=config['output'],
        output_path=os.path.join(test_debug_dir, f"{config['name']}_rendered.png"),
        glyph="AaBb",
        size=600,
        position=(100, 100),
        image_size=(800, 800)
    )
    
    # Verify output file exists and has content
    assert os.path.exists(config['output']), f"Output file {config['output']} was not created"
    assert os.path.getsize(config['output']) > 0, f"Output file {config['output']} is empty"


def test_file_size_comparison(setup_test_environment):
    """Compare file sizes across all rendering modes."""
    results = []
    
    for config in test_configs:
        file_size = os.path.getsize(config['output'])
        results.append({
            "name": config['name'],
            "size_kb": file_size / 1024
        })
    
    # Calculate reduction percentages relative to original mode
    original_size = next(r['size_kb'] for r in results if r['name'] == 'original')
    
    # Print results
    print("\nFile Size Comparison Results:")
    print("-" * 50)
    print(f"{'Mode':<20} {'Size (KB)':<12} {'Reduction':<10}")
    print("-" * 50)
    
    for result in results:
        reduction = (1 - result['size_kb'] / original_size) * 100
        print(f"{result['name']:<20} {result['size_kb']:<12.2f} {reduction:>8.2f}%")
    
    print("-" * 50)
    print(f"\nTest completed. Debug images saved to: {DEBUG_DIR}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
     