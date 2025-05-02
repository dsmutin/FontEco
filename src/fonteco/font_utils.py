"""Font utility functions for subsetting and manipulating fonts.

This module provides functions for creating font subsets containing specific
character sets (e.g., alphanumeric, Cyrillic) and other font manipulation
utilities.
"""

from fontTools.subset import Subsetter
from fontTools.ttLib import TTFont


def subset_font_to_alphanumeric(font_path):
    """
    Subset a font to only include alphanumeric characters [a-zA-Z0-9] and space.
    
    Args:
        font_path (str): Path to the input font file
        
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
        input_font_path (str): Path to the input font file
        output_font_path (str): Path where the subsetted font will be saved
        subset_function (callable): Function to use for subsetting
        
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


def subset_font_to_single_glyph(font_path, glyph_name="A"):
    """
    Create a subset of a font containing only a single glyph.
    
    Args:
        font_path (str): Path to the input font file
        glyph_name (str): Name of the glyph to include (default: "A")
        
    Returns:
        TTFont: A subsetted font containing only the specified glyph and required glyphs
        
    Raises:
        FileNotFoundError: If the input font file does not exist
        ValueError: If the input file is not a valid font file or if the glyph is not found
    """
    # Load the font
    font = TTFont(font_path)
    
    # If glyph_name is a single character, convert it to glyph name
    unicode_value = None
    if len(glyph_name) == 1:
        unicode_value = ord(glyph_name)
        # Try to get the glyph name from cmap
        for table in font['cmap'].tables:
            if unicode_value in table.cmap:
                glyph_name = table.cmap[unicode_value]
                break
    
    # Get the glyph order
    glyph_order = font.getGlyphOrder()
    
    # Find the glyph index
    glyph_index = None
    for i, name in enumerate(glyph_order):
        if name == glyph_name:
            glyph_index = i
            break
    
    if glyph_index is None:
        raise ValueError(f"Glyph {glyph_name} not found in font")
    
    # Create a new font with minimal tables
    from fontTools.ttLib import newTable
    new_font = TTFont()
    
    # First set up glyf and loca tables
    new_font['glyf'] = newTable('glyf')
    new_font['glyf'].glyphs = {}
    new_font['loca'] = newTable('loca')
    
    # Copy required glyphs
    if 'glyf' in font:
        # Copy .notdef glyph if it exists
        if '.notdef' in font['glyf'].glyphs:
            new_font['glyf'].glyphs['.notdef'] = font['glyf']['.notdef']
        # Copy target glyph
        if glyph_name in font['glyf'].glyphs:
            new_font['glyf'].glyphs[glyph_name] = font['glyf'][glyph_name]
    
    # Set glyph order first
    glyph_order = ['.notdef', glyph_name]
    new_font.setGlyphOrder(glyph_order)
    
    # Copy and update other required tables
    for tag in ['head', 'hhea', 'maxp', 'OS/2', 'hmtx', 'name', 'post']:
        if tag in font:
            new_font[tag] = newTable(tag)
            new_font[tag] = font[tag]  # Direct table copy
    
    # Create a new cmap table
    new_font['cmap'] = newTable('cmap')
    new_font['cmap'].tableVersion = 0
    new_font['cmap'].tables = []
    
    # Create a format 4 subtable (Unicode BMP)
    from fontTools.ttLib.tables._c_m_a_p import CmapSubtable
    format4 = CmapSubtable.newSubtable(4)
    format4.platformID = 3
    format4.platEncID = 1
    format4.language = 0
    
    # Add the mapping
    if unicode_value is not None:
        format4.cmap = {unicode_value: glyph_name}
    else:
        format4.cmap = {}
    
    # Add the subtable to the cmap
    new_font['cmap'].tables.append(format4)
    
    # Update maxp table
    if 'maxp' in new_font:
        new_font['maxp'].numGlyphs = len(glyph_order)
    
    # Update hmtx table
    if 'hmtx' in new_font:
        hmtx = new_font['hmtx']
        # Keep only the metrics for our glyphs
        hmtx.metrics = {name: hmtx.metrics[name] for name in glyph_order if name in hmtx.metrics}
    
    return new_font