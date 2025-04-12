from fontTools.ttLib import TTFont
from fonteco.font_utils import subset_font_to_cyrillic_and_numbers

def main():
    # Input and output paths
    input_font_path = "fonts/Roboto.ttf"
    output_font_path = "fonts/Roboto_subset.ttf"
    
    try:
        # Create the subset font
        subset_font = subset_font_to_cyrillic_and_numbers(input_font_path)
        
        # Save the subset font
        subset_font.save(output_font_path)
        print(f"Created Cyrillic subset font at: {output_font_path}")
        
    except FileNotFoundError:
        print(f"Error: Could not find input font at {input_font_path}")
    except Exception as e:
        print(f"Error creating subset font: {e}")

if __name__ == "__main__":
    main() 