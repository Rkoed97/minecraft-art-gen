"""Drawing tools: paint and erase.

Tools operate purely on PixelImage data — no GUI dependency.
Each tool accumulates pixel changes during a stroke and commits them as a batch.
"""

from enum import Enum, auto

from minecraft_art_gen.models.pixel_image import PixelImage, TRANSPARENT

RGBA = tuple[int, int, int, int]


class ToolType(Enum):
    PEN = auto()
    ERASER = auto()


class Stroke:
    """A single paint/erase stroke: a set of affected pixel coordinates."""

    def __init__(self) -> None:
        # Maps (x, y) -> old color, so undo can reverse
        self._before: dict[tuple[int, int], RGBA] = {}
        self._after: dict[tuple[int, int], RGBA] = {}

    def record(self, x: int, y: int, old_color: RGBA, new_color: RGBA) -> None:
        if (x, y) not in self._before:
            self._before[(x, y)] = old_color
        self._after[(x, y)] = new_color

    @property
    def is_empty(self) -> bool:
        return not self._after

    def apply(self, image: PixelImage) -> PixelImage:
        coords = list(self._after.keys())
        new_img = image
        for x, y in coords:
            new_img = new_img.set_pixel(x, y, self._after[(x, y)])
        return new_img

    def revert(self, image: PixelImage) -> PixelImage:
        new_img = image
        for (x, y), color in self._before.items():
            new_img = new_img.set_pixel(x, y, color)
        return new_img


class PaintTool:
    """Left-click/drag tool: paints pixels with the current color."""

    def __init__(self) -> None:
        self._current_stroke: Stroke | None = None

    def begin(self, image: PixelImage, x: int, y: int, color: RGBA) -> PixelImage:
        self._current_stroke = Stroke()
        return self._paint(image, x, y, color)

    def drag(self, image: PixelImage, x: int, y: int, color: RGBA) -> PixelImage:
        if self._current_stroke is None:
            self._current_stroke = Stroke()
        return self._paint(image, x, y, color)

    def end(self) -> Stroke | None:
        stroke = self._current_stroke
        self._current_stroke = None
        return stroke if (stroke and not stroke.is_empty) else None

    def _paint(self, image: PixelImage, x: int, y: int, color: RGBA) -> PixelImage:
        if not (0 <= x < image.width and 0 <= y < image.height):
            return image
        old = image.get_pixel(x, y)
        if old == color:
            return image
        assert self._current_stroke is not None
        self._current_stroke.record(x, y, old, color)
        return image.set_pixel(x, y, color)


class EraseTool:
    """Right-click/drag tool: erases pixels to transparent."""

    def __init__(self) -> None:
        self._current_stroke: Stroke | None = None

    def begin(self, image: PixelImage, x: int, y: int) -> PixelImage:
        self._current_stroke = Stroke()
        return self._erase(image, x, y)

    def drag(self, image: PixelImage, x: int, y: int) -> PixelImage:
        if self._current_stroke is None:
            self._current_stroke = Stroke()
        return self._erase(image, x, y)

    def end(self) -> Stroke | None:
        stroke = self._current_stroke
        self._current_stroke = None
        return stroke if (stroke and not stroke.is_empty) else None

    def _erase(self, image: PixelImage, x: int, y: int) -> PixelImage:
        if not (0 <= x < image.width and 0 <= y < image.height):
            return image
        old = image.get_pixel(x, y)
        if old == TRANSPARENT:
            return image
        assert self._current_stroke is not None
        self._current_stroke.record(x, y, old, TRANSPARENT)
        return image.clear_pixel(x, y)
