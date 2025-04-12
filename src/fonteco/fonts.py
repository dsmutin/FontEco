from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFont
from .dithering import generate_sobol_sequence, apply_blue_noise_dithering
from .glyphs import image_to_glyph

def perforate_font(input_font_path:str, output_font_path:str, reduction_percentage:float, with_bug:bool, draw_images:bool, scale_factor:float, test:bool):
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
    
    for glyph_name in glyphs:
        glyph = font["glyf"][glyph_name]
        if glyph.isComposite() or glyph_name == ".notdef" or glyph_name not in font.getReverseGlyphMap():
            print(f"Skipping glyph {glyph_name}: composite.")
            # Skip composite glyphs (e.g., accented characters) or .notdef or not in UNICODE
            continue

        # Find the Unicode character for this glyph
        unicode_char = None
        for code, name in cmap.items():
            if name == glyph_name:
                unicode_char = chr(code)
                break

        if not unicode_char:
            print(f"Skipping glyph {glyph_name}: No Unicode mapping found.")
            continue

        # Clear the image for the next glyph
        draw.rectangle([0, 0, image_size[0], image_size[1]], fill=255)

        # Render the glyph to the image
        draw.text((50, 50), unicode_char, font=pil_font,
                  fill=0)  # Adjusted position

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

            print("trace: ", glyph_name)
        except Exception as e:
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