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

def create_subset_font(input_font_path, output_font_path, subset_function):
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
    subsetted_font = subset_function(input_font_path)
    
    # Save the subsetted font
    subsetted_font.save(output_font_path)

def subset_font_to_alphanumeric_and_cyrillic(font_path):
    """
    Create a subset of the font containing only Cyrillic characters, numbers, and common punctuation.
    
    Args:
        font_path (str): Path to the input font file
        
    Returns:
        TTFont: A subset of the original font containing only Cyrillic characters, numbers, and punctuation
    """
    # Load the font
    font = TTFont(font_path)
    
    # Create a subsetter
    subsetter = Subsetter()
    
    # Define the characters to keep
    chars_to_keep = set()
    
    # Add alphanumeric characters
    for i in range(0x0030, 0x003A):
        chars_to_keep.add(i)
    for i in range(0x0061, 0x007B):  # a-z
        chars_to_keep.add(i)
    for i in range(0x0041, 0x005B):  # A-Z
        chars_to_keep.add(i)
    
    # Add basic Latin punctuation
    for i in range(0x0020, 0x0030):  # space, !"#$%&'()*+,-./
        chars_to_keep.add(i)
    for i in range(0x003A, 0x0041):  # :;<=>?@
        chars_to_keep.add(i)
    for i in range(0x005B, 0x0061):  # [\]^_`
        chars_to_keep.add(i)
    for i in range(0x007B, 0x007F):  # {|}~
        chars_to_keep.add(i)
    
    # Add Cyrillic characters
    for i in range(0x0400, 0x0500):  # Cyrillic block
        chars_to_keep.add(i)
    
    # Add specific symbols
    specific_symbols = "!@#$%^&*()\":;`~|/.,\\"
    for char in specific_symbols:
        chars_to_keep.add(ord(char))
    
    # Configure the subsetter
    subsetter.populate(unicodes=chars_to_keep)
    
    # Subset the font
    subsetter.subset(font)
    
    return font