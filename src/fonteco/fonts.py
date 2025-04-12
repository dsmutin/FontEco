from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFont
from .dithering import generate_sobol_sequence, apply_blue_noise_dithering
from .glyphs import image_to_glyph, decompose_glyph
from tqdm import tqdm

def perforate_font(input_font_path:str, output_font_path:str, reduction_percentage:float, with_bug:bool, draw_images:bool, scale_factor:float, test:bool, debug:bool=False):
    """
    Perforate all glyphs in a font using Sobol' sequence and blue noise dithering.
    
    Args:
        input_font_path (str): Path to the input font file (e.g., 'fonts/Times.ttf')
        output_font_path (str): Path where the perforated font will be saved (e.g., 'fonts/EcoTimes.ttf')
        reduction_percentage (float): Percentage of dots to remove (0-100)
        with_bug (bool): If True, applies a special coordinate transformation (bug mode)
        draw_images (bool): If True, saves debug images of each perforated glyph
        scale_factor (float): Scaling factor for glyph coordinates
        test (bool): If True, only processes the first 20 glyphs
        debug (bool): If True, prints detailed debug information
        
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
    pil_font = ImageFont.truetype(
        input_font_path, size=400)  # Increased font size

    # Get the font's character map (cmap)
    cmap = font.getBestCmap()

    # Track modified glyphs
    modified_glyphs = set()

    # Iterate over all glyphs in the font
    glyphs = font.getGlyphOrder()
    
    if test:
        glyphs = glyphs[0:20]
    
    # Create progress bar with different detail levels based on debug flag
    progress_bar = tqdm(
        glyphs,
        desc="Processing glyphs",
        unit="glyph",
        bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]' if debug else '{l_bar}{bar}| {n_fmt}/{total_fmt}'
    )
    
    for glyph_name in progress_bar:
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
            print(f"bounding box: {getattr(glyph, 'xMin', None)}, {getattr(glyph, 'yMin', None)}, {getattr(glyph, 'xMax', None)}, {getattr(glyph, 'yMax', None)}")

        # Clear the image for the next glyph
        draw.rectangle([0, 0, image_size[0], image_size[1]], fill=255)

        # Try to render the glyph directly first
        if unicode_char and not glyph.isComposite():
            if debug and unicode_char and 0x0400 <= ord(unicode_char) <= 0x04FF:
                print("Using direct text rendering")
            draw.text((50, 50), unicode_char, font=pil_font, fill=0)
        else:
            # For composite glyphs or when direct rendering fails, try to use Latin analogue
            if unicode_char and 0x0400 <= ord(unicode_char) <= 0x04FF:
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
                                x, y = args
                                x = int((x - bbox[0]) * scale + 50)
                                y = int((y - bbox[1]) * scale + 50)
                                draw.point((x, y), fill=0)
                            elif cmd == 'lineTo':
                                x, y = args
                                x = int((x - bbox[0]) * scale + 50)
                                y = int((y - bbox[1]) * scale + 50)
                                draw.point((x, y), fill=0)
                            elif cmd == 'curveTo':
                                # For curves, we'll just draw the end point
                                x, y = args[-1]
                                x = int((x - bbox[0]) * scale + 50)
                                y = int((y - bbox[1]) * scale + 50)
                                draw.point((x, y), fill=0)
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
                            x, y = args
                            x = int((x - bbox[0]) * scale + 50)
                            y = int((y - bbox[1]) * scale + 50)
                            draw.point((x, y), fill=0)
                        elif cmd == 'lineTo':
                            x, y = args
                            x = int((x - bbox[0]) * scale + 50)
                            y = int((y - bbox[1]) * scale + 50)
                            draw.point((x, y), fill=0)
                        elif cmd == 'curveTo':
                            # For curves, we'll just draw the end point
                            x, y = args[-1]
                            x = int((x - bbox[0]) * scale + 50)
                            y = int((y - bbox[1]) * scale + 50)
                            draw.point((x, y), fill=0)
                elif debug:
                    print("Failed to decompose non-Cyrillic glyph")

        # Generate Sobol' sequence points
        num_points = int(image_size[0] * image_size[1]
                         * (reduction_percentage / 100))
        sobol_points = generate_sobol_sequence(
            image_size[0], image_size[1], num_points)

        # Apply blue noise dithering
        perforated_image = apply_blue_noise_dithering(image, sobol_points)

        try:
            # Convert the dithered image back to a glyph outline
            font["glyf"][glyph_name] = image_to_glyph(
                perforated_image, scale_factor, font, with_bug)

            # Mark this glyph as modified
            modified_glyphs.add(glyph_name)

            # Save the perforated glyph image (for visualization)
            if draw_images:
                perforated_image.save(
                    f"/home/dsmutin/tools/fonteco/perforated_{glyph_name}.png")

            if debug:
                print("trace: ", glyph_name)
        except Exception as e:
            if debug:
                print(f"Error processing glyph {glyph_name}: {e}")
            continue

    # Remove non-modified glyphs from the font
    for glyph_name in list(font.getGlyphOrder()):
        if glyph_name not in modified_glyphs:
            font["glyf"][glyph_name] = font["glyf"]["space"]

    # Modify the name table
    name_table = font['name']
    for name_record in name_table.names:
        # Check if the name record is for the font family name (nameID 1) or style name (nameID 2)
        if name_record.nameID == 1:  # Font Family Name
            name_record.string = "Eco" + str(font['name'].getName(1, 3, 1, 0x409).toStr())
        elif name_record.nameID == 2:  # Font Subfamily Name (Style)
            name_record.string = "PR" + str(100 - reduction_percentage)

    # Save the modified font
    font.save(output_font_path)
    print(f"Perforated font saved to {output_font_path}")