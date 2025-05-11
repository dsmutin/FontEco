"""Font perforation implementation.

This module provides functionality for perforating fonts by removing dots from
glyphs while maintaining readability. It uses blue noise dithering and Sobol'
sequences to create visually pleasing patterns.
"""

from typing import Union
from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFont
from tqdm import tqdm
import os

from .dithering import generate_sobol_sequence, apply_blue_noise_dithering, apply_shape_dithering
from .glyphs import image_to_glyph, decompose_glyph


def perforate_font(
    input_font_path: str,
    output_font_path: str,
    reduction_percentage: float = 20,
    point_size: int = 1,
    with_bug: bool = False,
    draw_images: bool = False,
    scale_factor: Union[float, str] = "AUTO",
    test: bool = False,
    debug: bool = False,
    progress_callback = None,
    dithering_mode: str = "blue_noise",
    render_mode: str = "original",
    num_levels: int = 2,
    debug_dir: str = None,
    shape_type: str = "circle",
    shape_size: Union[int, str] = 10,
    margin: int = 1
):
    """
    Perforate all glyphs in a font using Sobol' sequence and blue noise dithering.
    
    Args:
        input_font_path (str): Path to the input font file
        output_font_path (str): Path where the perforated font will be saved
        reduction_percentage (float): Percentage of dots to remove (0-100)
        point_size (int): Size of each point to remove (default: 1)
        with_bug (bool): If True, applies a special coordinate transformation
        draw_images (bool): If True, saves debug images of each perforated glyph
        scale_factor (float | str): Scaling factor for glyph coordinates
        test (bool): If True, only processes the first 20 glyphs
        debug (bool): If True, prints detailed debug information
        progress_callback: Optional callback function to report progress (0-100)
        dithering_mode (str): Dithering mode to use:
            - "blue_noise": Uses Sobol' sequence and blue noise dithering
            - "shape": Uses shape-based dithering with circles or rectangles
        render_mode (str): Rendering mode to use for glyph conversion:
            - "original": Uses Potrace's default path tracing
            - "simplified": Reduces the number of transparency levels (optimal: 4 levels)
            - "optimized": Uses point clustering and path optimization (optimal: 100 grid size)
            - "optimized_masked": Like optimized but ensures paths stay within glyph boundaries
            - "shape": Uses shape-based dithering with circles or rectangles
        num_levels (int): Number of transparency levels for simplified mode (optimal: 4)
                         or grid size for optimized mode (optimal: 100)
        debug_dir (str): Directory to save debug images (if None, no debug images are saved)
        shape_type (str): Type of shape to use for shape dithering ("circle" or "rectangle")
        shape_size (int or str): Size of shapes for shape dithering:
            - int: exact size
            - "random": random size between margin*2 and max possible
            - "biggest": biggest possible size that fits
        margin (int): Minimum margin between shapes and edges for shape dithering
        
    Returns:
        None
        
    Raises:
        FileNotFoundError: If the input font file does not exist
        ValueError: If reduction_percentage is not between 0 and 100
        TypeError: If any of the arguments have incorrect types
    """
    # Load the font
    font = TTFont(input_font_path)

    # Create a temporary image to render the glyphs
    image_size = (512, 512)  # Increased size for better scaling
    image = Image.new("L", image_size, 255)  # White background
    draw = ImageDraw.Draw(image)

    # Load the font into PIL for rendering
    pil_font = ImageFont.truetype(input_font_path, size=400)

    # Get the font's character map (cmap)
    cmap = font.getBestCmap()

    # Track modified glyphs
    modified_glyphs = set()

    # Special handling for problematic Cyrillic characters
    cyrillic_special_cases = {
        'uni041D': 'H',  # Н
        'uni041F': 'P',  # П
        'uni042D': 'E',  # Э
        'uni042F': 'R',  # Я
        'uni044D': 'e',  # э
        'uni044F': 'r',  # я
        'uni0401': 'E',  # Ё
        'uni0451': 'e',  # ё
        'uni0419': 'N',  # Й
        'uni0439': 'n',  # й
    }

    # Iterate over all glyphs in the font
    glyphs = font.getGlyphOrder()
    
    if test:
        glyphs = glyphs[0:20]
    
    total_glyphs = len(glyphs)
    
    # Create progress bar with different detail levels based on debug flag
    progress_bar = tqdm(
        glyphs,
        desc="Processing glyphs",
        unit="glyph",
        bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]' if debug else '{l_bar}{bar}| {n_fmt}/{total_fmt}'
    )
    
    for i, glyph_name in enumerate(progress_bar):
        if progress_callback:
            progress = int((i / total_glyphs) * 100)
            progress_callback(progress)
            
        glyph = font["glyf"][glyph_name]
        if glyph_name == ".notdef" or glyph_name not in font.getReverseGlyphMap():
            if debug:
                print(f"Skipping glyph {glyph_name}: not in Unicode map.")
            continue

        # Find the Unicode character for this glyph
        unicode_char = None
        for code, name in cmap.items():
            if name == glyph_name:
                unicode_char = chr(code)
                break

        # Debug output for Cyrillic characters
        if debug and unicode_char and 0x0400 <= ord(unicode_char) <= 0x04FF:
            print(f"\nProcessing Cyrillic glyph: {glyph_name}")
            print(f"Unicode: {ord(unicode_char):04X}")
            print(f"isComposite: {glyph.isComposite()}")
            print(f"has contours: {hasattr(glyph, 'endPtsOfContours')}")
            if hasattr(glyph, 'endPtsOfContours'):
                print(f"number of contours: {len(glyph.endPtsOfContours)}")
            print(f"bounding box: {getattr(glyph, 'xMin', None)}, "
                  f"{getattr(glyph, 'yMin', None)}, "
                  f"{getattr(glyph, 'xMax', None)}, "
                  f"{getattr(glyph, 'yMax', None)}")

        # Clear the image for the next glyph
        draw.rectangle([0, 0, image_size[0], image_size[1]], fill=255)

        # Try to render the glyph directly first
        if unicode_char and not glyph.isComposite():
            if debug and unicode_char and 0x0400 <= ord(unicode_char) <= 0x04FF:
                print("Using direct text rendering")
            draw.text((50, 50), unicode_char, font=pil_font, fill=0)
        else:
            # For composite glyphs or when direct rendering fails, try special cases first
            if glyph_name in cyrillic_special_cases:
                if debug:
                    print(f"Using special case for {glyph_name}: "
                          f"{cyrillic_special_cases[glyph_name]}")
                draw.text((50, 50), cyrillic_special_cases[glyph_name],
                         font=pil_font, fill=0)
            elif unicode_char and 0x0400 <= ord(unicode_char) <= 0x04FF:
                # Map Cyrillic to Latin analogues
                cyrillic_to_latin = {
                    0x0410: 'A', 0x0412: 'B', 0x0415: 'E', 0x0417: '3',
                    0x0418: 'N', 0x041A: 'K', 0x041C: 'M', 0x041E: 'O',
                    0x0420: 'P', 0x0421: 'C', 0x0422: 'T', 0x0423: 'Y',
                    0x0425: 'X', 0x0430: 'a', 0x0435: 'e', 0x043E: 'o',
                    0x0440: 'p', 0x0441: 'c', 0x0443: 'y', 0x0445: 'x'
                }
                latin_char = cyrillic_to_latin.get(ord(unicode_char))
                if latin_char:
                    if debug:
                        print(f"Using Latin analogue: {latin_char}")
                    draw.text((50, 50), latin_char, font=pil_font, fill=0)
                else:
                    if debug:
                        print("No Latin analogue found, trying decomposition")
                    # If no Latin analogue, try decomposition
                    pen = decompose_glyph(glyph, font.getGlyphSet())
                    if pen:
                        if debug:
                            print("Using decomposition for rendering")
                        # Get the glyph's bounding box
                        bbox = glyph.xMin, glyph.yMin, glyph.xMax, glyph.yMax
                        # Calculate scaling factors to fit in our image
                        scale_x = (image_size[0] - 100) / (bbox[2] - bbox[0])
                        scale_y = (image_size[1] - 100) / (bbox[3] - bbox[1])
                        scale = min(scale_x, scale_y)
                        
                        # Draw the decomposed glyph
                        for cmd, args in pen.value:
                            if cmd == 'moveTo':
                                point_x, point_y = args
                                point_x = int((point_x - bbox[0]) * scale + 50)
                                point_y = int((point_y - bbox[1]) * scale + 50)
                                draw.point((point_x, point_y), fill=0)
                            elif cmd == 'lineTo':
                                point_x, point_y = args
                                point_x = int((point_x - bbox[0]) * scale + 50)
                                point_y = int((point_y - bbox[1]) * scale + 50)
                                draw.point((point_x, point_y), fill=0)
                            elif cmd == 'curveTo':
                                # For curves, we'll just draw the end point
                                point_x, point_y = args[-1]
                                point_x = int((point_x - bbox[0]) * scale + 50)
                                point_y = int((point_y - bbox[1]) * scale + 50)
                                draw.point((point_x, point_y), fill=0)
                    elif debug:
                        print("Failed to decompose glyph")
            else:
                # For non-Cyrillic composite glyphs, try decomposition
                pen = decompose_glyph(glyph, font.getGlyphSet())
                if pen:
                    if debug:
                        print("Using decomposition for non-Cyrillic glyph")
                    # Get the glyph's bounding box
                    bbox = glyph.xMin, glyph.yMin, glyph.xMax, glyph.yMax
                    # Calculate scaling factors to fit in our image
                    scale_x = (image_size[0] - 100) / (bbox[2] - bbox[0])
                    scale_y = (image_size[1] - 100) / (bbox[3] - bbox[1])
                    scale = min(scale_x, scale_y)
                    
                    # Draw the decomposed glyph
                    for cmd, args in pen.value:
                        if cmd == 'moveTo':
                            point_x, point_y = args
                            point_x = int((point_x - bbox[0]) * scale + 50)
                            point_y = int((point_y - bbox[1]) * scale + 50)
                            draw.point((point_x, point_y), fill=0)
                        elif cmd == 'lineTo':
                            point_x, point_y = args
                            point_x = int((point_x - bbox[0]) * scale + 50)
                            point_y = int((point_y - bbox[1]) * scale + 50)
                            draw.point((point_x, point_y), fill=0)
                        elif cmd == 'curveTo':
                            # For curves, we'll just draw the end point
                            point_x, point_y = args[-1]
                            point_x = int((point_x - bbox[0]) * scale + 50)
                            point_y = int((point_y - bbox[1]) * scale + 50)
                            draw.point((point_x, point_y), fill=0)
                elif debug:
                    print("Failed to decompose non-Cyrillic glyph")

        # Generate Sobol' sequence points
        num_points = int(image_size[0] * image_size[1]
                         * (reduction_percentage / 100))
        sobol_points = generate_sobol_sequence(
            image_size[0], image_size[1], num_points)

        # Apply dithering based on render mode
        if dithering_mode == "shape":
            perforated_image = apply_shape_dithering(
                image, 
                shape_type=shape_type,
                margin=margin,
                shape_size=shape_size,
                reduction_percentage=reduction_percentage
            )
        else:
            perforated_image = apply_blue_noise_dithering(image, sobol_points, point_size)

        try:
            # Convert the dithered image back to a glyph outline
            font["glyf"][glyph_name] = image_to_glyph(
                perforated_image, scale_factor, font, with_bug,
                render_mode=render_mode,
                num_levels=num_levels,
                debug_dir=os.path.join(debug_dir, glyph_name) if debug_dir else None
            )

            # Mark this glyph as modified
            modified_glyphs.add(glyph_name)

            # Save the perforated glyph image (for visualization)
            if draw_images:
                perforated_image.save(
                    f"/home/dsmutin/tools/fonteco/perforated_{glyph_name}.png")

            if debug:
                print("trace: ", glyph_name)
        except Exception as exc:
            if debug:
                print(f"Error processing glyph {glyph_name}: {exc}")
                continue

    # Remove non-modified glyphs from the font
    for glyph_name in list(font.getGlyphOrder()):
        if glyph_name not in modified_glyphs:
            font["glyf"][glyph_name] = font["glyf"]["space"]

    # Modify the name table
    name_table = font['name']
    if debug:
        print("\nProcessing font names:")
        print("Available name records:")
        for name_record in name_table.names:
            print(f"  ID: {name_record.nameID}, Platform: {name_record.platformID}, "
                  f"Encoding: {name_record.platEncID}, Language: {name_record.langID}")
    
    for name_record in name_table.names:
        try:
            if debug:
                print(f"\nProcessing name record {name_record.nameID}:")
                print(f"  Platform: {name_record.platformID}")
                print(f"  Encoding: {name_record.platEncID}")
                print(f"  Language: {name_record.langID}")
                print(f"  Raw string: {name_record.string}")
            
            if name_record.nameID == 1:  # Font Family name      
                original_name = name_record.string.decode('utf-16-be') if isinstance(name_record.string, bytes) else name_record.string
                name_record.string = f"{original_name} Eco"
                if debug:
                    print(f"  Modified family name: {name_record.string}")
            elif name_record.nameID == 4:  # Full font name
                original_name = name_record.string.decode('utf-16-be') if isinstance(name_record.string, bytes) else name_record.string
                name_record.string = f"{original_name} Eco"
                if debug:
                    print(f"  Modified full name: {name_record.string}")
        except UnicodeDecodeError:
            if debug:
                print(f"  Warning: UTF-16-BE decoding failed for name record {name_record.nameID}")
            # If UTF-16-BE decoding fails, try other encodings or use a default name
            if name_record.nameID == 1:  # Font Family name
                name_record.string = "Font Eco"
            elif name_record.nameID == 4:  # Full font name
                name_record.string = "Font Eco"
        except Exception as e:
            if debug:
                print(f"  Warning: Could not modify font name record {name_record.nameID}: {e}")
            continue

    # Save the modified font
    font.save(output_font_path)
    print(f"Perforated font saved to {output_font_path}")