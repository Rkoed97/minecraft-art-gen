"""In-memory RGBA pixel image model.

All mutating operations return a NEW PixelImage — the original is never modified.
"""

TRANSPARENT: tuple[int, int, int, int] = (0, 0, 0, 0)


class PixelImage:
    """Immutable-style RGBA pixel buffer.

    Internally uses a flat list of (r, g, b, a) tuples.
    Coordinates are 0-based, origin at top-left.
    """

    def __init__(self, width: int, height: int, fill: tuple[int, int, int, int] = TRANSPARENT) -> None:
        if width <= 0 or height <= 0:
            raise ValueError(f"Dimensions must be positive, got {width}x{height}")
        self._width = width
        self._height = height
        self._pixels: list[tuple[int, int, int, int]] = [fill] * (width * height)

    # ------------------------------------------------------------------
    # Factories
    # ------------------------------------------------------------------

    @classmethod
    def from_data(cls, width: int, height: int, pixels: list[tuple[int, int, int, int]]) -> "PixelImage":
        """Create from a pre-built pixel list (must have width*height entries)."""
        if len(pixels) != width * height:
            raise ValueError(
                f"Expected {width * height} pixels, got {len(pixels)}"
            )
        img = cls.__new__(cls)
        img._width = width
        img._height = height
        img._pixels = list(pixels)
        return img

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def width(self) -> int:
        return self._width

    @property
    def height(self) -> int:
        return self._height

    @property
    def size(self) -> tuple[int, int]:
        return (self._width, self._height)

    # ------------------------------------------------------------------
    # Pixel access
    # ------------------------------------------------------------------

    def _index(self, x: int, y: int) -> int:
        if not (0 <= x < self._width and 0 <= y < self._height):
            raise IndexError(f"Pixel ({x}, {y}) out of bounds for {self._width}x{self._height} image")
        return y * self._width + x

    def get_pixel(self, x: int, y: int) -> tuple[int, int, int, int]:
        return self._pixels[self._index(x, y)]

    def set_pixel(self, x: int, y: int, color: tuple[int, int, int, int]) -> "PixelImage":
        """Return a new PixelImage with the pixel at (x, y) set to color."""
        _validate_color(color)
        new_pixels = list(self._pixels)
        new_pixels[self._index(x, y)] = color
        return PixelImage.from_data(self._width, self._height, new_pixels)

    def set_pixels(self, coords: list[tuple[int, int]], color: tuple[int, int, int, int]) -> "PixelImage":
        """Return a new PixelImage with all listed coordinates set to color. Efficient bulk update."""
        _validate_color(color)
        new_pixels = list(self._pixels)
        for x, y in coords:
            new_pixels[self._index(x, y)] = color
        return PixelImage.from_data(self._width, self._height, new_pixels)

    def clear_pixel(self, x: int, y: int) -> "PixelImage":
        """Return a new PixelImage with the pixel at (x, y) set to transparent."""
        return self.set_pixel(x, y, TRANSPARENT)

    def clear_pixels(self, coords: list[tuple[int, int]]) -> "PixelImage":
        """Return a new PixelImage with all listed coordinates set to transparent."""
        return self.set_pixels(coords, TRANSPARENT)

    # ------------------------------------------------------------------
    # Resize
    # ------------------------------------------------------------------

    def resize(self, new_width: int, new_height: int) -> "PixelImage":
        """Return a new PixelImage of the given size.

        Pixels in the overlapping region are copied; new areas are transparent.
        """
        if new_width <= 0 or new_height <= 0:
            raise ValueError(f"Dimensions must be positive, got {new_width}x{new_height}")
        new_img = PixelImage(new_width, new_height)
        new_pixels = list(new_img._pixels)
        copy_w = min(self._width, new_width)
        copy_h = min(self._height, new_height)
        for y in range(copy_h):
            for x in range(copy_w):
                new_pixels[y * new_width + x] = self._pixels[y * self._width + x]
        return PixelImage.from_data(new_width, new_height, new_pixels)

    # ------------------------------------------------------------------
    # PIL interop
    # ------------------------------------------------------------------

    def to_pil_image(self):
        """Convert to a PIL Image in RGBA mode."""
        from PIL import Image  # lazy import to keep model PIL-independent in tests

        pil_img = Image.new("RGBA", (self._width, self._height))
        pil_img.putdata(self._pixels)  # type: ignore[arg-type]
        return pil_img

    @classmethod
    def from_pil_image(cls, pil_image) -> "PixelImage":
        """Create a PixelImage from a PIL Image (any mode — converted to RGBA)."""
        rgba = pil_image.convert("RGBA")
        width, height = rgba.size
        pixels = list(rgba.get_flattened_data())
        return cls.from_data(width, height, pixels)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, PixelImage):
            return NotImplemented
        return self._width == other._width and self._height == other._height and self._pixels == other._pixels

    def __repr__(self) -> str:
        return f"PixelImage({self._width}x{self._height})"


def _validate_color(color: tuple[int, int, int, int]) -> None:
    if len(color) != 4:
        raise ValueError(f"Color must be (r, g, b, a), got {color!r}")
    for i, channel in enumerate(color):
        if not (0 <= channel <= 255):
            raise ValueError(f"Color channel {i} out of range [0, 255]: {channel}")
