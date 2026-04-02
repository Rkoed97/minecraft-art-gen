# minecraft-art-gen

A Python package for creating and editing Minecraft mod asset textures programmatically.

[![PyPI](https://img.shields.io/pypi/v/minecraft-art-gen)](https://pypi.org/project/minecraft-art-gen/)
[![Python](https://img.shields.io/pypi/pyversions/minecraft-art-gen)](https://pypi.org/project/minecraft-art-gen/)
[![CI](https://github.com/Rkoed97/minecraft-art-gen/actions/workflows/ci.yml/badge.svg)](https://github.com/Rkoed97/minecraft-art-gen/actions/workflows/ci.yml)

---

## Installation

```bash
pip install minecraft-art-gen
```

Requires Python 3.10+.

---

## Quick start

```python
from minecraft_art_gen.models.pixel_image import PixelImage
from minecraft_art_gen.models.asset_type import ASSET_TYPES
from minecraft_art_gen.editor.tools import PaintTool
from minecraft_art_gen.io.png_writer import save_png
from minecraft_art_gen.io.png_reader import load_png

# Create a blank 16x16 block texture
asset = ASSET_TYPES["block"]
img = PixelImage(asset.default_width, asset.default_height)

# Paint a pixel (immutable — returns a new image each call)
tool = PaintTool()
img = tool.begin(img, x=0, y=0, color=(255, 0, 0, 255))   # red
img = tool.drag(img, x=1, y=0, color=(255, 0, 0, 255))
stroke = tool.end()  # Stroke object — can be used for undo

# Save and reload
save_png(img, "my_block.png")
img2 = load_png("my_block.png")
```

---

## API reference

### `PixelImage`

Immutable RGBA pixel grid.

```python
from minecraft_art_gen.models.pixel_image import PixelImage, TRANSPARENT

img = PixelImage(width=16, height=16)          # blank (transparent) canvas
img = PixelImage.from_pil_image(pil_img)       # from a Pillow Image

color = img.get_pixel(x, y)                    # -> (r, g, b, a)
img2  = img.set_pixel(x, y, (r, g, b, a))     # returns new PixelImage
pil   = img.to_pil_image()                     # -> PIL.Image (RGBA)
```

> All mutating operations return a **new** `PixelImage`; the original is never modified.

---

### Asset types

```python
from minecraft_art_gen.models.asset_type import ASSET_TYPES, ASSET_TYPE_ORDER

# List all supported types in display order
for key in ASSET_TYPE_ORDER:
    a = ASSET_TYPES[key]
    print(a.name, a.default_size, a.variants)
```

| Key | Name | Default size | Extra variants |
|---|---|---|---|
| `block` | Block | 16×16 | 32, 64, 128, 256 |
| `item` | Item | 16×16 | 32, 64, 128 |
| `entity_classic` | Entity (Classic Mob) | 64×32 | — |
| `entity_humanoid` | Entity (Humanoid) | 64×64 | — |
| `gui` | GUI Element | 256×256 | — |
| `effect_icon` | Effect Icon | 18×18 | — |
| `painting_small` | Painting (1×1) | 16×16 | — |
| `painting_medium` | Painting (2×1) | 32×16 | — |
| `painting_wide` | Painting (3×1) | 48×16 | — |
| `painting_large` | Painting (4×2) | 64×32 | — |
| `painting_grand` | Painting (4×4) | 64×64 | — |
| `particle` | Particle | 8×8 | — |
| `trim` | Armor Trim | 16×32 | 32×64, 64×128 |

---

### Drawing tools

Tools are stateless with respect to the image — they operate on `PixelImage` and return new instances.

```python
from minecraft_art_gen.editor.tools import PaintTool, EraseTool, Stroke

# PaintTool — sets pixels to a color
paint = PaintTool()
img = paint.begin(img, x, y, color=(255, 128, 0, 255))
img = paint.drag(img, x+1, y, color=(255, 128, 0, 255))
stroke: Stroke = paint.end()

# EraseTool — sets pixels to transparent
erase = EraseTool()
img = erase.begin(img, x, y)
stroke = erase.end()

# Stroke — undo / redo support
img = stroke.revert(img)   # undo the stroke
img = stroke.apply(img)    # redo the stroke
```

---

### File I/O

```python
from minecraft_art_gen.io.png_reader import load_png
from minecraft_art_gen.io.png_writer import save_png

img = load_png("texture.png")    # raises ValueError on invalid path/file
save_png(img, "output.png")      # atomic write (temp file → rename)
```

---

## GUI application

This package also ships a full pixel-art editor GUI. To launch it:

```bash
minecraft-art-gen
```

> The GUI requires PySide6. It is installed automatically as a dependency.
> See the [`master`](https://github.com/Rkoed97/minecraft-art-gen/tree/master) branch for app-focused documentation.

---

## Development

```bash
git clone git@github.com:Rkoed97/minecraft-art-gen.git
cd minecraft-art-gen
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest tests/
```

---

## License

MIT
