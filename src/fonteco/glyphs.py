"""Glyph manipulation and conversion utilities.

This module provides functions for working with font glyphs, including:
- Decomposing composite glyphs
- Converting images to glyph outlines
- Generating and applying dithering patterns
"""

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from fontTools.misc.transform import Transform
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont
from scipy.stats import qmc
import cv2
import potrace
import os
import warnings


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


def generate_sobol_sequence(width, height, num_points):
    """
    Generate a Sobol' sequence of points within the given dimensions.
    
    Args:
        width (int): Width of the area to generate points in
        height (int): Height of the area to generate points in
        num_points (int): Number of points to generate (must be a power of 2)
        
    Returns:
        numpy.ndarray: Array of shape (num_points, 2) containing the generated points
    """
    sampler = qmc.Sobol(d=2, scramble=True)
    points = sampler.random_base2(m=int(np.log2(num_points)))
    points = qmc.scale(points, [0, 0], [width, height])
    return points.astype(int)


def apply_blue_noise_dithering(image, sobol_points):
    """
    Apply blue noise dithering by removing dots based on the Sobol' sequence.
    
    Args:
        image (PIL.Image.Image): Input grayscale image to dither
        sobol_points (numpy.ndarray): Array of points from Sobol' sequence
        
    Returns:
        PIL.Image.Image: Dithered image with white pixels at Sobol' sequence points
    """
    pixels = image.load()
    width, height = image.size
    for point_x, point_y in sobol_points:
        if 0 <= point_x < width and 0 <= point_y < height:
            pixels[point_x, point_y] = 255  # Set pixel to white (remove dot)
    return image


def test_perforation(input_font_path, output_test_path, reduction_percentage):
    """
    Test the perforation process on a sample glyph.
    
    Args:
        input_font_path (str): Path to the input font file
        output_test_path (str): Path to save the test output image
        reduction_percentage (float): Percentage of dots to remove (0-100)
    """
    # Load the font
    font = TTFont(input_font_path)

    # Create a temporary image to render the font glyphs
    image_size = (800, 800)  # Size of the image for rendering glyphs
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


def image_to_glyph(image, scale_factor, font, with_bug, render_mode="original", num_levels=4, debug_dir=None, debug=False):
    """
    Convert a dithered image to a glyph outline and update the font.
    
    Args:
        image (PIL.Image.Image): Input image to convert to glyph
        scale_factor (float or str): Either a numeric value for manual scaling or "AUTO" for automatic scaling
        font (fontTools.ttLib.TTFont): Font object to update with the new glyph
        with_bug (bool): If True, applies a special coordinate transformation
        render_mode (str): Rendering mode to use ("original", "simplified", or "optimized")
        num_levels (int): Number of transparency levels for simplified mode (optimal: 4)
                         or grid size for optimized mode (optimal: 100)
        debug_dir (str): Directory to save debug images (if None, no debug images are saved)
        debug (bool): If True, print debug information about the conversion process
        
    Returns:
        fontTools.ttLib.tables._g_l_y_f.Glyph: The converted glyph
        
    Raises:
        ValueError: If the glyph has too many contours (> 65535)
        TypeError: If scale_factor is neither a number nor "AUTO"
    """
    # Save initial image if debug is enabled
    if debug_dir:
        os.makedirs(debug_dir, exist_ok=True)
        image.save(os.path.join(debug_dir, "1_initial.png"))

    # Convert PIL Image to NumPy array (OpenCV format)
    img = np.array(image)

    if debug:
        print(f"\nImage to glyph conversion debug:")
        print(f"Initial image shape: {img.shape}")
        print(f"Initial image min/max values: {img.min()}/{img.max()}")
        print(f"Number of unique values: {len(np.unique(img))}")

    # Invert colors (Potrace expects black-on-white)
    img = cv2.bitwise_not(img)

    # Resize the image if necessary
    if img.shape[0] > 512 or img.shape[1] > 512:
        img = cv2.resize(img, (256, 256), interpolation=cv2.INTER_AREA)

    # Save dithered image if debug is enabled
    if debug_dir:
        cv2.imwrite(os.path.join(debug_dir, "2_dithered.png"), img)

    # Apply simplification if using simplified mode
    if render_mode == "simplified":
        if num_levels < 4:
            warnings.warn(
                "Using num_levels < 4 in simplified mode may result in blank glyphs. "
                "It is recommended to use at least 4 levels for proper rendering.",
                UserWarning
            )
        from .dithering import simplify_image
        simplified_img = simplify_image(Image.fromarray(img), num_levels, debug=debug)
        img = np.array(simplified_img)
        
        if debug:
            print(f"\nAfter simplification:")
            print(f"Image shape: {img.shape}")
            print(f"Image min/max values: {img.min()}/{img.max()}")
            print(f"Number of unique values: {len(np.unique(img))}")
        
        # Save simplified image if debug is enabled
        if debug_dir:
            cv2.imwrite(os.path.join(debug_dir, "3_simplified.png"), img)

    # Threshold to binary (black/white)
    _, binary_img = cv2.threshold(img, 128, 1, cv2.THRESH_BINARY)

    if debug:
        print(f"\nAfter thresholding:")
        print(f"Binary image shape: {binary_img.shape}")
        print(f"Binary image min/max values: {binary_img.min()}/{binary_img.max()}")
        print(f"Number of unique values: {len(np.unique(binary_img))}")

    # Ensure the image is in the correct format for Potrace
    binary_img = binary_img.astype(np.uint8)

    # Save binary image if debug is enabled
    if debug_dir:
        cv2.imwrite(os.path.join(debug_dir, "4_binary.png"), binary_img * 255)

    try:
        # Trace the image with Potrace
        bitmap = potrace.Bitmap(binary_img)
        path = bitmap.trace()

        if debug:
            print(f"\nAfter tracing:")
            print(f"Number of paths: {len(path)}")
            for i, curve in enumerate(path):
                print(f"Path {i}: {len(curve.segments)} segments")

        # Initialize a new glyph pen
        pen = TTGlyphPen(font.getGlyphSet())

        if render_mode == "optimized":
            if num_levels < 50:
                warnings.warn(
                    "Using num_levels < 50 in optimized mode may result in poor glyph quality. "
                    "It is recommended to use at least 100 for proper rendering.",
                    UserWarning
                )
            # Collect all points from all paths
            all_points = []
            for curve in path:
                points = [curve.start_point]
                for segment in curve.segments:
                    if segment.is_corner:
                        points.extend([segment.c, segment.end_point])
                    else:
                        points.extend([segment.c1, segment.c2, segment.end_point])
                all_points.extend(points)
            
            # Convert to numpy array for easier processing
            points_array = np.array(all_points)
            
            # Calculate bounding box
            min_x, min_y = points_array.min(axis=0)
            max_x, max_y = points_array.max(axis=0)
            
            # Create a grid for point clustering
            grid_size = num_levels  # Use num_levels as grid_size for optimized mode
            x_bins = np.linspace(min_x, max_x, grid_size)
            y_bins = np.linspace(min_y, max_y, grid_size)
            
            # Assign points to grid cells
            x_indices = np.digitize(points_array[:, 0], x_bins)
            y_indices = np.digitize(points_array[:, 1], y_bins)
            
            # Group points by grid cell
            grid_points = {}
            for i, (x_idx, y_idx) in enumerate(zip(x_indices, y_indices)):
                cell = (x_idx, y_idx)
                if cell not in grid_points:
                    grid_points[cell] = []
                grid_points[cell].append(points_array[i])
            
            # Calculate centroids for each grid cell
            centroids = []
            for cell_points in grid_points.values():
                if len(cell_points) > 0:
                    centroid = np.mean(cell_points, axis=0)
                    centroids.append(centroid)
            
            centroids = np.array(centroids)
            if len(centroids) > 0:
                # Nearest-neighbor path construction
                visited = np.zeros(len(centroids), dtype=bool)
                path_order = [0]
                visited[0] = True
                for _ in range(1, len(centroids)):
                    last = centroids[path_order[-1]]
                    dists = np.linalg.norm(centroids - last, axis=1)
                    dists[visited] = np.inf
                    next_idx = np.argmin(dists)
                    path_order.append(next_idx)
                    visited[next_idx] = True
                ordered_centroids = centroids[path_order]
                # Draw path
                pen.moveTo((ordered_centroids[0][0], ordered_centroids[0][1]))
                for pt in ordered_centroids[1:]:
                    pen.lineTo((pt[0], pt[1]))
                pen.closePath()
        else:
            # Original path processing
            for curve in path:
                start = curve.start_point
                pen.moveTo((start[0], start[1]))
                for segment in curve.segments:
                    if segment.is_corner:
                        pen.lineTo((segment.c[0], segment.c[1]))
                        pen.lineTo((segment.end_point[0], segment.end_point[1]))
                    else:
                        pen.curveTo(
                            (segment.c1[0], segment.c1[1]),
                            (segment.c2[0], segment.c2[1]),
                            (segment.end_point[0], segment.end_point[1]),
                        )
                pen.closePath()

        # Get the glyph from the pen
        glyph = pen.glyph()

        # Simplify the glyph outline if necessary
        if len(glyph.endPtsOfContours) > 65535:
            raise ValueError("Too many contours in glyph outline")

        if debug:
            print(f"\nFinal glyph:")
            print(f"Number of contours: {len(glyph.endPtsOfContours)}")
            print(f"Number of points: {len(glyph.coordinates)}")

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
            image_height = img.shape[0]
            final_scale_factor = units_per_em / image_height
        else:
            final_scale_factor = float(scale_factor)

        if debug:
            print(f"\nScaling:")
            print(f"Units per em: {units_per_em}")
            print(f"Ascender: {ascender}")
            print(f"Descender: {descender}")
            print(f"Final scale factor: {final_scale_factor}")

        # Scale the glyph coordinates
        for i in range(len(glyph.coordinates)):
            if not with_bug:
                glyph.coordinates[i] = (
                    int(glyph.coordinates[i][0] * final_scale_factor),
                    int(glyph.coordinates[i][1] * -final_scale_factor + ascender)
                )
            else:
                glyph.coordinates[i] = (
                    int(glyph.coordinates[-i][0] * final_scale_factor),
                    int(glyph.coordinates[-i][1] * final_scale_factor)
                )

        return glyph
    except Exception as e:
        if debug:
            print(f"Error during glyph processing: {e}")
        # Return a simple space glyph as fallback
        return font["glyf"]["space"]