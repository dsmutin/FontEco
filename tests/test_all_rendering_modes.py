"""Test for all font rendering modes.

This module tests and compares original, simplified, and optimized rendering modes
to evaluate their effects on font size and quality.
"""

import os
from fontTools.ttLib import TTFont
from fonteco.fonts import perforate_font
from fonteco.render_ttf import render_glyph_to_image
from fonteco.font_utils import create_subset_font, subset_font_to_glyphs


def test_all_rendering_modes():
    """Test and compare all rendering modes."""
    # Input and output paths
    input_font = "fonts/Times.ttf"
    subset_font = "fonts/test.ttf"
    debug_dir = "test_outputs/debug_all_modes"
    
    # Create output directories
    os.makedirs("test_outputs", exist_ok=True)
    os.makedirs(debug_dir, exist_ok=True)
    
    # Create subset with specified glyphs
    print("Creating font subset...")
    glyphs = ['A', 'a', 'B', 'b', ' ']  # Test with more glyphs
    create_subset_font(input_font, subset_font, lambda f: subset_font_to_glyphs(f, glyphs))
    
    # Test configurations
    test_configs = [
        {
            "name": "original",
            "render_mode": "original",
            "num_levels": None,
            "output": "test_outputs/original_mode.ttf"
        },
        {
            "name": "simplified_optimal",
            "render_mode": "simplified",
            "num_levels": 4,  # Optimal value for simplified mode
            "output": "test_outputs/simplified_mode_optimal.ttf"
        },
        {
            "name": "optimized_optimal",
            "render_mode": "optimized",
            "num_levels": 100,  # Optimal value for optimized mode
            "output": "test_outputs/optimized_mode_optimal.ttf"
        },
        {
            "name": "optimized_masked",
            "render_mode": "optimized_masked",
            "num_levels": 100,  # Using same grid size as optimal optimized mode
            "output": "test_outputs/optimized_mode_masked.ttf"
        },
        {
            "name": "optimized_aggressive",
            "render_mode": "optimized",
            "num_levels": 50,  # More aggressive optimization
            "output": "test_outputs/optimized_mode_aggressive.ttf"
        }
    ]
    
    # Run tests for each configuration
    results = []
    for config in test_configs:
        print(f"\nTesting {config['name']} mode...")
        try:
            perforate_font(
                input_font_path=subset_font,
                output_font_path=config['output'],
                reduction_percentage=90,
                with_bug=False,
                draw_images=True,
                scale_factor="AUTO",
                test=False,
                debug=True,
                point_size=1,
                render_mode=config['render_mode'],
                num_levels=config['num_levels'],
                debug_dir=os.path.join(debug_dir, config['name'])
            )
            
            # Render comparison image
            render_glyph_to_image(
                font_path=config['output'],
                output_path=os.path.join(debug_dir, f"{config['name']}_rendered.png"),
                glyph="AaBb",
                size=600,
                position=(100, 100),
                image_size=(800, 800)
            )
            
            # Get file size
            file_size = os.path.getsize(config['output'])
            results.append({
                "name": config['name'],
                "size_kb": file_size / 1024
            })
        except Exception as e:
            print(f"Error processing {config['name']}: {e}")
            continue
    
    # Print results
    print("\nResults:")
    print("-" * 50)
    print(f"{'Mode':<20} {'Size (KB)':<12} {'Reduction':<10}")
    print("-" * 50)
    
    # Calculate reduction percentages relative to original mode
    original_size = next(r['size_kb'] for r in results if r['name'] == 'original')
    for result in results:
        reduction = (1 - result['size_kb'] / original_size) * 100
        print(f"{result['name']:<20} {result['size_kb']:<12.2f} {reduction:>8.2f}%")
    
    print("-" * 50)
    print(f"\nTest completed. Debug images saved to: {debug_dir}")


if __name__ == "__main__":
    test_all_rendering_modes() 