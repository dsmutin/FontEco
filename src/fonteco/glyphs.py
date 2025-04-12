from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
import numpy as np
import cv2
import potrace
from PIL import Image, ImageDraw

def decompose_glyph(glyph, glyph_set):
    """
    Decompose a composite glyph into its components.
    
    Args:
        glyph (fontTools.ttLib.tables._g_l_y_f.Glyph): The glyph to decompose
        glyph_set (fontTools.ttLib.ttFont._TTGlyphSet): Set of glyphs in the font
        
    Returns:
        RecordingPen or None: A pen containing the decomposed glyph data if the glyph is composite,
                             None if the glyph is not composite
    """
    if glyph.isComposite():
        pen = RecordingPen()
        glyph.draw(pen, glyph_set)
        return pen
    return None

from fontTools.misc.transform import Transform
from fontTools.pens.recordingPen import RecordingPen
import numpy as np
from fontTools.ttLib import TTFont
from scipy.stats import qmc  # For Sobol' sequence generation
from PIL import Image, ImageDraw, ImageFont
import potrace
from fontTools.pens.ttGlyphPen import TTGlyphPen
import cv2


def generate_sobol_sequence(width, height, num_points):
    """
    Generate a Sobol' sequence of points within the given dimensions.
    """
    sampler = qmc.Sobol(d=2, scramble=True)
    points = sampler.random_base2(m=int(np.log2(num_points)))
    points = qmc.scale(points, [0, 0], [width, height])
    return points.astype(int)


def apply_blue_noise_dithering(image, sobol_points):
    """
    Apply blue noise dithering by removing dots based on the Sobol' sequence.
    """
    pixels = image.load()
    width, height = image.size
    for x, y in sobol_points:
        if 0 <= x < width and 0 <= y < height:
            pixels[x, y] = 255  # Set pixel to white (remove dot)
    return image


def test_perforation(input_font_path, output_test_path, reduction_percentage):
    """
    Perforate a font using Sobol' sequence and blue noise dithering.
    """
    # Load the font
    font = TTFont(input_font_path)

    # Create a temporary image to render the font glyphs
    image_size = (512, 512)  # Size of the image for rendering glyphs
    image = Image.new("L", image_size, 255)  # White background
    draw = ImageDraw.Draw(image)

    # Generate Sobol' sequence points
    num_points = int(image_size[0] * image_size[1]
                     * (reduction_percentage / 100))
    sobol_points = generate_sobol_sequence(
        image_size[0], image_size[1], num_points)

    # Load the font into PIL for rendering
    pil_font = ImageFont.truetype(input_font_path, size=500)

    # Render the text to get the glyphs
    draw.text((10, 10), "A", font=pil_font, fill=0)  # Render a sample glyph

    # Apply blue noise dithering
    perforated_image = apply_blue_noise_dithering(image, sobol_points)
    # Save the perforated image (for visualization)
    perforated_image.save(output_test_path)

    print(f"Perforated font saved to {output_test_path}")


def image_to_glyph(image, scale_factor, font, with_bug):
    """
    Convert a dithered image to a glyph outline and update the font.
    
    Args:
        image (PIL.Image.Image): Input image to convert to glyph
        scale_factor (float or str): Either a numeric value for manual scaling or "AUTO" for automatic scaling
        font (fontTools.ttLib.TTFont): Font object to update with the new glyph
        with_bug (bool): If True, applies a special coordinate transformation (bug mode)
        
    Returns:
        fontTools.ttLib.tables._g_l_y_f.Glyph: The converted glyph
        
    Raises:
        ValueError: If the glyph has too many contours (> 65535)
        TypeError: If scale_factor is neither a number nor "AUTO"
    """
    # Convert PIL Image to NumPy array (OpenCV format)
    img = np.array(image)

    # Invert colors (Potrace expects black-on-white)
    img = cv2.bitwise_not(img)

    # Resize the image if necessary
    if img.shape[0] > 512 or img.shape[1] > 512:
        img = cv2.resize(img, (256, 256), interpolation=cv2.INTER_AREA)

    # Threshold to binary (black/white)
    _, binary_img = cv2.threshold(
        img, 128, 1, cv2.THRESH_BINARY)  # Use 1 instead of 255

    # Ensure the image is in the correct format for Potrace
    binary_img = binary_img.astype(np.uint8)  # Ensure data type is uint8

    # Debug: Save the binary image
    # Scale back to 0-255 for visualization
    cv2.imwrite("debug_binary.png", binary_img * 255)

    # Trace the image with Potrace
    bitmap = potrace.Bitmap(binary_img)
    path = bitmap.trace()

    # Initialize a new glyph pen
    pen = TTGlyphPen(font.getGlyphSet())

    # Iterate over Potrace paths and convert to glyph outline
    for curve in path:
        start = curve.start_point
        pen.moveTo((start[0], start[1]))  # Unpack tuple (x, y)
        for segment in curve.segments:
            if segment.is_corner:
                pen.lineTo((segment.c[0], segment.c[1]))  # Unpack tuple (x, y)
                # Unpack tuple (x, y)
                pen.lineTo((segment.end_point[0], segment.end_point[1]))
            else:
                pen.curveTo(
                    (segment.c1[0], segment.c1[1]),  # Unpack tuple (x, y)
                    (segment.c2[0], segment.c2[1]),  # Unpack tuple (x, y)
                    # Unpack tuple (x, y)
                    (segment.end_point[0], segment.end_point[1]),
                )
        pen.closePath()

    # Get the glyph from the pen
    glyph = pen.glyph()

    # Simplify the glyph outline if necessary
    if len(glyph.endPtsOfContours) > 65535:
        raise ValueError("Too many contours in glyph outline")

    # Get font metrics for automatic scaling
    head_table = font['head']
    units_per_em = head_table.unitsPerEm
    hhea_table = font['hhea']
    ascender = hhea_table.ascender
    descender = hhea_table.descender
    
    # Calculate the actual height of the glyph in font units
    glyph_height = ascender - descender
    
    # Determine the scale factor to use
    if scale_factor == "AUTO":
        # Calculate the scale factor based on the image size and font metrics
        # We want the glyph to maintain its original proportions relative to the em square
        image_height = img.shape[0]
        final_scale_factor = units_per_em / image_height
    else:
        # Use the provided numeric scale factor
        final_scale_factor = float(scale_factor)

    # Scale the glyph coordinates to fit within the TrueType format limits
    for i in range(len(glyph.coordinates)):
        if not with_bug:
            glyph.coordinates[i] = (int(glyph.coordinates[i][0] * final_scale_factor),
                                    int(glyph.coordinates[i][1] * -final_scale_factor + ascender))
        else:
            # very beauterful bug
            glyph.coordinates[i] = (int(glyph.coordinates[-i][0] * final_scale_factor),
                                    int(glyph.coordinates[-i][1] * final_scale_factor))

    # Update the glyph in the font
    return glyph