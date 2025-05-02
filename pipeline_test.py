from src.fonteco.fonts import perforate_font
from src.fonteco.testing import visualize_perforation
import os

# Test configurations
TEST_CONFIGS = [
    {
        "name": "default",
        "point_size": 1,
        "size_reduction": 1.0
    },
    {
        "name": "large_points",
        "point_size": 2,
        "size_reduction": 1.0
    },
    {
        "name": "reduced_size",
        "point_size": 1,
        "size_reduction": 0.8
    },
    {
        "name": "combined",
        "point_size": 2,
        "size_reduction": 0.8
    }
]

INPUT_FONT_PATH = "fonts/TimesNewRoman_subset.ttf"
REDUCTION_PERCENTAGE = 40
OUTPUT_DIR = "test_outputs"

def main():
    """Run the font perforation test pipeline."""
    # Create output directory if it doesn't exist
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Run tests for each configuration
    for config in TEST_CONFIGS:
        print(f"\nTesting configuration: {config['name']}")
        
        # Generate output paths
        output_font_path = os.path.join(OUTPUT_DIR, f"EcoTimesNewRoman_{config['name']}.ttf")
        test_image_path = os.path.join(OUTPUT_DIR, f"test_{config['name']}.png")
        
        # Run visualization
        visualize_perforation(
            INPUT_FONT_PATH,
            test_image_path,
            REDUCTION_PERCENTAGE
        )
        
        # Perforate font with current configuration
        perforate_font(
            input_font_path=INPUT_FONT_PATH,
            output_font_path=output_font_path,
            reduction_percentage=REDUCTION_PERCENTAGE,
            point_size=config['point_size'],
            size_reduction=config['size_reduction']
        )
        
        print(f"Completed {config['name']} configuration")

if __name__ == "__main__":
    main() 