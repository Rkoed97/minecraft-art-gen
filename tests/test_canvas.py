"""Widget-level tests for the pixel canvas using pytest-qt."""

import pytest
from PySide6.QtCore import Qt, QPoint, QPointF
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication

from minecraft_art_gen.editor.canvas import PixelCanvas, CELL_SIZE
from minecraft_art_gen.models.pixel_image import PixelImage, TRANSPARENT

RED = (255, 0, 0, 255)
GREEN = (0, 255, 0, 255)


@pytest.fixture
def canvas(qtbot):
    c = PixelCanvas()
    c.resize(400, 400)
    qtbot.addWidget(c)
    c.show()
    return c


def _pixel_to_viewport(canvas: PixelCanvas, px: int, py: int) -> QPoint:
    """Convert texture pixel coords to viewport coords (center of cell)."""
    scene_x = px * CELL_SIZE + CELL_SIZE // 2
    scene_y = py * CELL_SIZE + CELL_SIZE // 2
    return canvas.mapFromScene(scene_x, scene_y)


class TestCanvasInit:
    def test_default_image_size(self, canvas):
        assert canvas._image.size == (16, 16)

    def test_initial_zoom_is_100pct(self, canvas):
        assert canvas._zoom == pytest.approx(1.0)


class TestSetImage:
    def test_set_image_updates_size(self, canvas, qtbot):
        img = PixelImage(8, 8)
        canvas.set_image(img)
        assert canvas._image.size == (8, 8)

    def test_set_image_clears_undo(self, canvas, qtbot):
        # Paint something to build undo history
        img = PixelImage(4, 4)
        canvas.set_image(img)
        vp = _pixel_to_viewport(canvas, 0, 0)
        qtbot.mousePress(canvas.viewport(), Qt.MouseButton.LeftButton, pos=vp)
        qtbot.mouseRelease(canvas.viewport(), Qt.MouseButton.LeftButton, pos=vp)
        # Now set new image — undo stack should be empty
        canvas.set_image(PixelImage(4, 4))
        assert canvas.undo() is None


class TestPainting:
    def test_left_click_paints_pixel(self, canvas, qtbot):
        img = PixelImage(16, 16)
        canvas.set_image(img)
        # Manually inject color (bypass parent widget color picker lookup)
        canvas._get_current_color = lambda: RED

        vp = _pixel_to_viewport(canvas, 2, 3)
        painted_images = []
        canvas.pixel_painted.connect(painted_images.append)

        qtbot.mousePress(canvas.viewport(), Qt.MouseButton.LeftButton, pos=vp)
        qtbot.mouseRelease(canvas.viewport(), Qt.MouseButton.LeftButton, pos=vp)

        assert len(painted_images) == 1
        assert painted_images[0].get_pixel(2, 3) == RED

    def test_right_click_erases_pixel(self, canvas, qtbot):
        img = PixelImage(16, 16, fill=RED)
        canvas.set_image(img)

        vp = _pixel_to_viewport(canvas, 1, 1)
        erased_images = []
        canvas.pixel_painted.connect(erased_images.append)

        qtbot.mousePress(canvas.viewport(), Qt.MouseButton.RightButton, pos=vp)
        qtbot.mouseRelease(canvas.viewport(), Qt.MouseButton.RightButton, pos=vp)

        assert len(erased_images) == 1
        assert erased_images[0].get_pixel(1, 1) == TRANSPARENT


class TestZoom:
    def test_zoom_clamped_to_min(self, canvas):
        canvas._set_zoom(0.01)
        assert canvas._zoom >= canvas._zoom  # doesn't crash
        from minecraft_art_gen.editor.canvas import ZOOM_MIN
        canvas._zoom_by(0.0001)
        assert canvas._zoom >= ZOOM_MIN

    def test_zoom_clamped_to_max(self, canvas):
        from minecraft_art_gen.editor.canvas import ZOOM_MAX
        canvas._zoom_by(10000)
        assert canvas._zoom <= ZOOM_MAX

    def test_zoom_changed_signal(self, canvas, qtbot):
        zooms = []
        canvas.zoom_changed.connect(zooms.append)
        canvas._set_zoom(2.0)
        assert zooms[-1] == 200


class TestLargeImagePixmapMode:
    def test_large_image_uses_pixmap_mode(self, canvas, qtbot):
        img = PixelImage(128, 128)
        canvas.set_image(img)
        assert canvas._use_pixmap_mode is True
        assert canvas._pixmap_item is not None

    def test_small_image_uses_rect_mode(self, canvas, qtbot):
        img = PixelImage(16, 16)
        canvas.set_image(img)
        assert canvas._use_pixmap_mode is False
        assert len(canvas._rect_items) == 16 * 16

    def test_large_image_paint_emits_signal(self, canvas, qtbot):
        img = PixelImage(128, 128)
        canvas.set_image(img)
        canvas._get_current_color = lambda: RED

        vp = _pixel_to_viewport(canvas, 5, 5)
        painted_images = []
        canvas.pixel_painted.connect(painted_images.append)

        qtbot.mousePress(canvas.viewport(), Qt.MouseButton.LeftButton, pos=vp)
        qtbot.mouseRelease(canvas.viewport(), Qt.MouseButton.LeftButton, pos=vp)

        assert len(painted_images) == 1
        assert painted_images[0].get_pixel(5, 5) == RED


class TestUndoRedo:
    def test_undo_reverts_paint(self, canvas, qtbot):
        img = PixelImage(4, 4)
        canvas.set_image(img)
        canvas._get_current_color = lambda: RED

        vp = _pixel_to_viewport(canvas, 0, 0)
        qtbot.mousePress(canvas.viewport(), Qt.MouseButton.LeftButton, pos=vp)
        qtbot.mouseRelease(canvas.viewport(), Qt.MouseButton.LeftButton, pos=vp)
        assert canvas._image.get_pixel(0, 0) == RED

        result = canvas.undo()
        assert result is not None
        assert result.get_pixel(0, 0) == TRANSPARENT

    def test_redo_reapplies_stroke(self, canvas, qtbot):
        img = PixelImage(4, 4)
        canvas.set_image(img)
        canvas._get_current_color = lambda: RED

        vp = _pixel_to_viewport(canvas, 0, 0)
        qtbot.mousePress(canvas.viewport(), Qt.MouseButton.LeftButton, pos=vp)
        qtbot.mouseRelease(canvas.viewport(), Qt.MouseButton.LeftButton, pos=vp)
        canvas.undo()
        result = canvas.redo()
        assert result is not None
        assert result.get_pixel(0, 0) == RED

    def test_no_undo_when_empty(self, canvas):
        assert canvas.undo() is None

    def test_no_redo_when_empty(self, canvas):
        assert canvas.redo() is None
