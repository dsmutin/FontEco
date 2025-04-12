from PIL import Image, ImageDraw, ImageFont
from .dithering import generate_sobol_sequence, apply_blue_noise_dithering

def test_perforation(input_font_path, output_test_path, reduction_percentage):
    """
    Perforate a font using Sobol' sequence and blue noise dithering.
    """
    # Create a temporary image to render the font glyphs
    image_size = (800, 500)  # Size of the image for rendering glyphs
    image = Image.new("L", image_size, 255)  # White background
    draw = ImageDraw.Draw(image)

    # Generate Sobol' sequence points
    num_points = int(image_size[0] * image_size[1] * (reduction_percentage / 100))
    sobol_points = generate_sobol_sequence(image_size[0], image_size[1], num_points)

    # Load the font into PIL for rendering
    pil_font = ImageFont.truetype(input_font_path, size=600)

    # Render the text to get the glyphs
    draw.text((10, 10), "Aa", font=pil_font, fill=0)  # Render a sample glyph

    # Apply blue noise dithering
    perforated_image = apply_blue_noise_dithering(image, sobol_points)
    # Save the perforated image (for visualization)
    perforated_image.save(output_test_path)

    print(f"Perforated font saved to {output_test_path}") 