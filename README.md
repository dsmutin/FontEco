<div align="right">
  <img src="misc/ecofont_logo.png" alt="FontEco Logo" width="100"/>
</div>

# FontEco

FontEco is a Python tool for creating eco-friendly fonts by perforating existing fonts using Sobol' sequence and blue noise dithering techniques. This process reduces the amount of ink needed to print text while maintaining readability.

## Features

- Font subsetting to alphanumeric characters
- Blue noise dithering using Sobol' sequences
- Glyph perforation with configurable reduction percentage
- Support for both automatic and manual scaling
- Debug visualization of perforated glyphs

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/FontEco.git
cd FontEco
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Create a subset of your font (optional):
```python
from fonteco.font_utils import create_subset_font
create_subset_font('fonts/Times.ttf', 'fonts/Times_subset.ttf')
```

2. Perforate the font:
```python
from fonteco.fonts import perforate_font
perforate_font(
    input_font_path='fonts/Times.ttf',
    output_font_path='fonts/EcoTimes.ttf',
    reduction_percentage=15,
    with_bug=False,
    draw_images=True,
    scale_factor=3.5,
    test=False
)
```

## Parameters

- `reduction_percentage`: Percentage of dots to remove (0-100)
- `with_bug`: Enable special coordinate transformation (bug mode)
- `draw_images`: Save debug images of perforated glyphs
- `scale_factor`: Scaling factor for glyph coordinates
- `test`: Process only first 20 glyphs for testing

## Requirements

- Python 3.6+
- fontTools
- Pillow
- NumPy
- OpenCV
- potrace
- scipy

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. 