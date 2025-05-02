#!/usr/bin/env python3

import os
import sys

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from fonteco.font_utils import subset_font_to_glyphs

def main():
    # Define input and output paths
    input_font = os.path.join('fonts', 'Times.ttf')
    output_font = os.path.join('fonts', 'test.ttf')
    
    # Ensure the fonts directory exists
    os.makedirs(os.path.dirname(output_font), exist_ok=True)
    
    # Create subset with specified glyphs
    glyphs = ['a', 'A', ' ']
    subsetted_font = subset_font_to_glyphs(input_font, glyphs)
    
    # Save the subsetted font
    subsetted_font.save(output_font)
    print(f"Created subset font at: {output_font}")

if __name__ == '__main__':
    main() 