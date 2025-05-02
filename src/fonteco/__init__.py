"""Fonteco - A tool for creating perforated fonts.

Fonteco is a Python package that helps create perforated fonts by intelligently
removing dots from glyphs while maintaining readability. It uses blue noise
dithering techniques to ensure even distribution of removed dots.
"""

from .dithering import generate_sobol_sequence, apply_blue_noise_dithering
from .testing import visualize_perforation
from .glyphs import decompose_glyph, image_to_glyph
from .fonts import perforate_font
from .font_utils import (
    subset_font_to_alphanumeric,
    create_subset_font,
    subset_font_to_alphanumeric_and_cyrillic
)

__all__ = [
    'visualize_perforation',
    'generate_sobol_sequence',
    'apply_blue_noise_dithering',
    'decompose_glyph',
    'image_to_glyph',
    'perforate_font',
    'subset_font_to_alphanumeric',
    'create_subset_font',
    'subset_font_to_alphanumeric_and_cyrillic',
] 