# Minecraft Art Gen

A pixel-art editor for creating Minecraft mod asset textures, built with Python and Qt.

---

## Features

- **13 asset types** — blocks, items, entity skins, GUI elements, paintings, particles, armor trims, and more
- **Multi-resolution support** — create textures at standard (16×16) or higher resolutions for resource packs
- **Paint and erase tools** with per-stroke undo/redo
- **Zoom and pan** — Ctrl+scroll or Ctrl+`-`/`=` to zoom; middle-mouse drag to pan
- **Atomic PNG saves** — writes via a temp file so a failed save never corrupts existing work
- **Project manager** — organise multiple asset projects from a single workspace

---

## Requirements

- Python 3.10 or newer
- PySide6 (Qt 6.6+)
- Pillow 10+

---

## Installation

```bash
git clone git@github.com:Rkoed97/minecraft-art-gen.git
cd minecraft-art-gen

python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

pip install -e .
```

---

## Running the app

```bash
minecraft-art-gen
```

Or directly via Python:

```bash
python -m src.main
```

---

## Project structure

```
src/
├── app.py              Main window
├── main.py             Entry point
├── models/
│   ├── asset_type.py   Asset type definitions and size variants
│   └── pixel_image.py  Immutable RGBA pixel grid
├── editor/
│   ├── canvas.py       Zoomable pixel canvas (Qt widget)
│   ├── tools.py        Paint and erase tools with stroke recording
│   └── color_picker.py Color picker widget
├── screens/
│   ├── project_screen.py  Project selection and management
│   ├── asset_screen.py    Asset type picker
│   └── editor_screen.py   Main editing workspace
├── io/
│   ├── png_reader.py   Load PNG → PixelImage
│   └── png_writer.py   Save PixelImage → PNG (atomic)
└── utils/
    └── validators.py   Input and path validation
tests/                  pytest suite (95%+ coverage)
```

---

## Running tests

```bash
pip install -e ".[dev]"
pytest tests/
```

---

## Python module / PyPI

A PyPI-installable version of this project is available on the [`module`](https://github.com/Rkoed97/minecraft-art-gen/tree/module) branch, which exposes the core models, tools, and I/O as the `minecraft_art_gen` package.

---

## License

MIT
