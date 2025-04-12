from fontTools.subset import Subsetter
from fontTools.ttLib import TTFont
import re

def subset_font_to_alphanumeric(font_path):
    """
    Subset a font to only include alphanumeric characters [a-zA-Z0-9] and space.
    
    Args:
        font_path (str): Path to the input font file (e.g., 'fonts/Times.ttf')
        
    Returns:
        TTFont: A subsetted font containing only alphanumeric characters and space
        
    Raises:
        FileNotFoundError: If the input font file does not exist
        ValueError: If the input file is not a valid font file
    """
    # Load the font
    font = TTFont(font_path)
    
    # Create a subsetter
    subsetter = Subsetter()
    
    # Define the characters to keep (alphanumeric + space)
    chars_to_keep = set()
    
    # Add space character (Unicode 32)
    chars_to_keep.add(' ')
    
    # Add alphanumeric characters
    for char in range(ord('a'), ord('z') + 1):
        chars_to_keep.add(chr(char))
    for char in range(ord('A'), ord('Z') + 1):
        chars_to_keep.add(chr(char))
    for char in range(ord('0'), ord('9') + 1):
        chars_to_keep.add(chr(char))
    
    # Convert characters to Unicode strings
    unicodes = [ord(c) for c in chars_to_keep]
    
    # Add space glyph name explicitly to ensure it's included
    if 'space' in font.getGlyphOrder():
        subsetter.glyphs = ['space']
    
    # Configure the subsetter
    subsetter.populate(unicodes=unicodes)
    subsetter.subset(font)
    
    # Ensure space glyph exists
    if 'space' not in font.getGlyphOrder():
        # If space glyph is missing, create a minimal one
        space_glyph = font['glyf'].glyphs['.notdef'].__class__()
        font['glyf'].glyphs['space'] = space_glyph
        font['glyf'].glyphOrder.append('space')
    
    return font

def create_subset_font(input_font_path, output_font_path):
    """
    Create a subsetted font file containing only alphanumeric characters and space.
    
    Args:
        input_font_path (str): Path to the input font file (e.g., 'fonts/Times.ttf')
        output_font_path (str): Path where the subsetted font will be saved (e.g., 'fonts/Times_subset.ttf')
        
    Returns:
        None
        
    Raises:
        FileNotFoundError: If the input font file does not exist
        ValueError: If the input file is not a valid font file
        PermissionError: If there are permission issues writing the output file
    """
    # Create the subsetted font
    subsetted_font = subset_font_to_alphanumeric(input_font_path)
    
    # Save the subsetted font
    subsetted_font.save(output_font_path)

def subset_font_to_cyrillic_and_numbers(font_path):
    """
    Subset a font to only include Cyrillic characters and numbers.
    
    Args:
        font_path (str): Path to the input font file (e.g., 'fonts/Roboto.ttf')
        
    Returns:
        TTFont: A subsetted font containing only Cyrillic characters and numbers
        
    Raises:
        FileNotFoundError: If the input font file does not exist
        ValueError: If the input file is not a valid font file
    """
    # Load the font
    font = TTFont(font_path)
    
    # Create a subsetter
    subsetter = Subsetter()
    
    # Define the characters to keep (Cyrillic + numbers)
    chars_to_keep = set()
    
    # Add space character (Unicode 32)
    chars_to_keep.add(' ')
    
    # Add numbers
    for char in range(ord('0'), ord('9') + 1):
        chars_to_keep.add(chr(char))
    
    # Add alphanumeric characters
    for char in range(ord('a'), ord('z') + 1):
        chars_to_keep.add(chr(char))
    for char in range(ord('A'), ord('Z') + 1):
        chars_to_keep.add(chr(char))
        
    # Add Cyrillic characters (basic Cyrillic block)
    for char in range(0x0410, 0x044F + 1):  # А-я
        chars_to_keep.add(chr(char))
    
    # Convert characters to Unicode strings
    unicodes = [ord(c) for c in chars_to_keep]
    
    # Add space glyph name explicitly to ensure it's included
    if 'space' in font.getGlyphOrder():
        subsetter.glyphs = ['space']
    
    # Configure the subsetter
    subsetter.populate(unicodes=unicodes)
    subsetter.subset(font)
    
    # Ensure space glyph exists
    if 'space' not in font.getGlyphOrder():
        # If space glyph is missing, create a minimal one
        space_glyph = font['glyf'].glyphs['.notdef'].__class__()
        font['glyf'].glyphs['space'] = space_glyph
        font['glyf'].glyphOrder.append('space')
    
    return font 