"""Zoomable, scrollable pixel-art canvas.

Rendering strategy:
  - For textures <= 64x64: one QGraphicsRectItem per pixel (fast per-pixel updates).
  - For textures > 64x64: single QGraphicsPixmapItem backed by a QImage (fast bulk render).

Both strategies share the same mouse interaction logic.
"""

from __future__ import annotations

from PySide6.QtWidgets import (
    QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsPixmapItem,
)
from PySide6.QtCore import Signal, Qt, QPointF, QRectF
from PySide6.QtGui import (
    QColor, QPainter, QBrush, QPen, QPixmap, QImage, QKeySequence,
    QWheelEvent, QMouseEvent,
)

from minecraft_art_gen.models.pixel_image import PixelImage
from minecraft_art_gen.editor.tools import PaintTool, EraseTool, Stroke, ToolType

RGBA = tuple[int, int, int, int]

CELL_SIZE = 20          # screen pixels per texture pixel
GRID_COLOR = QColor(80, 80, 80, 120)
CHECKER_A = QColor(180, 180, 180)
CHECKER_B = QColor(120, 120, 120)
CHECKER_CELL = 8        # checker square size in screen pixels

ZOOM_MIN = 0.25
ZOOM_MAX = 40.0
ZOOM_STEP_KEY = 1.25
ZOOM_STEP_WHEEL = 1.15
UNDO_LIMIT = 100


class PixelCanvas(QGraphicsView):
    pixel_painted = Signal(PixelImage)   # emitted at end of stroke with committed image
    pixels_changed = Signal(PixelImage)  # emitted on every drag step
    cursor_moved = Signal(int, int)      # (x, y) in pixel coords; (-1,-1) when off canvas
    zoom_changed = Signal(int)           # zoom percentage

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._scene = QGraphicsScene(self)
        self.setScene(self._scene)

        # Rendering settings
        self.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, False)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setDragMode(QGraphicsView.DragMode.NoDrag)
        self.setBackgroundBrush(QBrush(QColor(40, 40, 40)))

        self._image: PixelImage = PixelImage(16, 16)
        self._zoom: float = 1.0
        self._use_pixmap_mode: bool = False

        # Item references (rect mode)
        self._rect_items: list[QGraphicsRectItem] = []
        # Item reference (pixmap mode)
        self._pixmap_item: QGraphicsPixmapItem | None = None

        # Tools
        self._paint_tool = PaintTool()
        self._erase_tool = EraseTool()
        self._active_tool: str = "none"  # "paint" | "erase" | "pan" | "none"
        self._selected_tool: ToolType = ToolType.PEN

        # Middle-mouse pan state
        self._pan_last: QPointF | None = None

        # Undo/redo stacks
        self._undo_stack: list[Stroke] = []
        self._redo_stack: list[Stroke] = []

        self._build_canvas()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def set_active_tool(self, tool: ToolType) -> None:
        self._selected_tool = tool

    def set_image(self, image: PixelImage) -> None:
        self._image = image
        self._undo_stack.clear()
        self._redo_stack.clear()
        self._rebuild_scene()

    def undo(self) -> PixelImage | None:
        if not self._undo_stack:
            return None
        stroke = self._undo_stack.pop()
        self._redo_stack.append(stroke)
        self._image = stroke.revert(self._image)
        self._refresh_pixels()
        return self._image

    def redo(self) -> PixelImage | None:
        if not self._redo_stack:
            return None
        stroke = self._redo_stack.pop()
        self._undo_stack.append(stroke)
        self._image = stroke.apply(self._image)
        self._refresh_pixels()
        return self._image

    # ------------------------------------------------------------------
    # Scene construction
    # ------------------------------------------------------------------

    def _rebuild_scene(self) -> None:
        self._scene.clear()
        self._rect_items = []
        self._pixmap_item = None
        self._use_pixmap_mode = (
            self._image.width > 64 or self._image.height > 64
        )
        self._build_canvas()

    def _build_canvas(self) -> None:
        w, h = self._image.width, self._image.height
        total_w = w * CELL_SIZE
        total_h = h * CELL_SIZE

        # Checkerboard background item (drawn once, never updated)
        checker = _build_checker_pixmap(w, h)
        checker_item = self._scene.addPixmap(checker)
        checker_item.setZValue(0)

        if self._use_pixmap_mode:
            self._pixmap_item = QGraphicsPixmapItem()
            self._pixmap_item.setZValue(1)
            self._scene.addItem(self._pixmap_item)
            self._refresh_pixels()
        else:
            self._rect_items = []
            no_pen = QPen(Qt.PenStyle.NoPen)
            for y in range(h):
                for x in range(w):
                    item = QGraphicsRectItem(
                        x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE
                    )
                    item.setPen(no_pen)
                    item.setBrush(QBrush(_to_qcolor(self._image.get_pixel(x, y))))
                    item.setZValue(1)
                    self._scene.addItem(item)
                    self._rect_items.append(item)

        # Grid overlay
        grid_pixmap = _build_grid_pixmap(w, h)
        grid_item = self._scene.addPixmap(grid_pixmap)
        grid_item.setZValue(2)

        self._scene.setSceneRect(QRectF(0, 0, total_w, total_h))

    def _refresh_pixels(self) -> None:
        if self._use_pixmap_mode:
            self._refresh_pixmap()
        else:
            self._refresh_rects()

    def _refresh_rects(self) -> None:
        w = self._image.width
        for y in range(self._image.height):
            for x in range(w):
                self._rect_items[y * w + x].setBrush(
                    QBrush(_to_qcolor(self._image.get_pixel(x, y)))
                )

    def _refresh_pixmap(self) -> None:
        if self._pixmap_item is None:
            return
        w, h = self._image.width, self._image.height
        qimg = QImage(w * CELL_SIZE, h * CELL_SIZE, QImage.Format.Format_ARGB32)
        qimg.fill(Qt.GlobalColor.transparent)
        painter = QPainter(qimg)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        for y in range(h):
            for x in range(w):
                color = _to_qcolor(self._image.get_pixel(x, y))
                painter.fillRect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE, color)
        painter.end()
        self._pixmap_item.setPixmap(QPixmap.fromImage(qimg))

    def _update_single_rect(self, x: int, y: int) -> None:
        """Fast single-pixel update in rect mode."""
        if self._use_pixmap_mode:
            return  # full refresh handled by calling code
        idx = y * self._image.width + x
        if 0 <= idx < len(self._rect_items):
            self._rect_items[idx].setBrush(
                QBrush(_to_qcolor(self._image.get_pixel(x, y)))
            )

    # ------------------------------------------------------------------
    # Mouse events
    # ------------------------------------------------------------------

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.MiddleButton:
            self._active_tool = "pan"
            self._pan_last = event.position()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()
            return

        pos = self._scene_to_pixel(event.position())
        if pos is None:
            super().mousePressEvent(event)
            return

        x, y = pos
        if event.button() == Qt.MouseButton.LeftButton:
            if self._selected_tool == ToolType.ERASER:
                self._active_tool = "erase"
                alpha = self._get_current_color()[3]
                self._image = self._erase_tool.begin(self._image, x, y, alpha)
            else:
                self._active_tool = "paint"
                color = self._get_current_color()
                self._image = self._paint_tool.begin(self._image, x, y, color)
            self._update_single_rect(x, y)
            if self._use_pixmap_mode:
                self._refresh_pixmap()
            self.pixels_changed.emit(self._image)
        elif event.button() == Qt.MouseButton.RightButton:
            self._active_tool = "erase"
            alpha = self._get_current_color()[3]
            self._image = self._erase_tool.begin(self._image, x, y, alpha)
            self._update_single_rect(x, y)
            if self._use_pixmap_mode:
                self._refresh_pixmap()
            self.pixels_changed.emit(self._image)
        event.accept()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self._active_tool == "pan" and self._pan_last is not None:
            delta = event.position() - self._pan_last
            self._pan_last = event.position()
            self.horizontalScrollBar().setValue(
                self.horizontalScrollBar().value() - int(delta.x())
            )
            self.verticalScrollBar().setValue(
                self.verticalScrollBar().value() - int(delta.y())
            )
            event.accept()
            return

        pos = self._scene_to_pixel(event.position())
        if pos is not None:
            x, y = pos
            self.cursor_moved.emit(x, y)
        else:
            self.cursor_moved.emit(-1, -1)

        if self._active_tool == "paint" and pos is not None:
            x, y = pos
            color = self._get_current_color()
            self._image = self._paint_tool.drag(self._image, x, y, color)
            self._update_single_rect(x, y)
            if self._use_pixmap_mode:
                self._refresh_pixmap()
            self.pixels_changed.emit(self._image)
        elif self._active_tool == "erase" and pos is not None:
            x, y = pos
            alpha = self._get_current_color()[3]
            self._image = self._erase_tool.drag(self._image, x, y, alpha)
            self._update_single_rect(x, y)
            if self._use_pixmap_mode:
                self._refresh_pixmap()
            self.pixels_changed.emit(self._image)
        event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if self._active_tool == "pan":
            self._active_tool = "none"
            self._pan_last = None
            self.setCursor(Qt.CursorShape.ArrowCursor)
            event.accept()
            return

        if self._active_tool == "paint":
            stroke = self._paint_tool.end()
            self._active_tool = "none"
            if stroke:
                self._push_undo(stroke)
                self.pixel_painted.emit(self._image)
        elif self._active_tool == "erase":
            stroke = self._erase_tool.end()
            self._active_tool = "none"
            if stroke:
                self._push_undo(stroke)
                self.pixel_painted.emit(self._image)
        event.accept()

    def leaveEvent(self, event) -> None:
        self.cursor_moved.emit(-1, -1)
        super().leaveEvent(event)

    # ------------------------------------------------------------------
    # Zoom
    # ------------------------------------------------------------------

    def wheelEvent(self, event: QWheelEvent) -> None:
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            if event.angleDelta().y() > 0:
                self._zoom_by(ZOOM_STEP_WHEEL)
            else:
                self._zoom_by(1.0 / ZOOM_STEP_WHEEL)
            event.accept()
        else:
            super().wheelEvent(event)

    def keyPressEvent(self, event) -> None:
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            key = event.key()
            if key in (Qt.Key.Key_Equal, Qt.Key.Key_Plus):
                self._zoom_by(ZOOM_STEP_KEY)
                event.accept()
                return
            if key == Qt.Key.Key_Minus:
                self._zoom_by(1.0 / ZOOM_STEP_KEY)
                event.accept()
                return
            if key == Qt.Key.Key_0:
                self._set_zoom(1.0)
                event.accept()
                return
        super().keyPressEvent(event)

    def _zoom_by(self, factor: float) -> None:
        new_zoom = max(ZOOM_MIN, min(ZOOM_MAX, self._zoom * factor))
        self._set_zoom(new_zoom)

    def _set_zoom(self, zoom: float) -> None:
        self._zoom = zoom
        self.resetTransform()
        self.scale(zoom, zoom)
        self.zoom_changed.emit(int(zoom * 100))

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _scene_to_pixel(self, viewport_pos: QPointF) -> tuple[int, int] | None:
        scene_pos = self.mapToScene(viewport_pos.toPoint())
        x = int(scene_pos.x() / CELL_SIZE)
        y = int(scene_pos.y() / CELL_SIZE)
        if 0 <= x < self._image.width and 0 <= y < self._image.height:
            return x, y
        return None

    def _get_current_color(self) -> RGBA:
        # Walk up the widget tree to find EditorScreen's color picker
        widget = self.parent()
        while widget is not None:
            if hasattr(widget, "_color_picker"):
                return widget._color_picker.current_color
            widget = widget.parent() if hasattr(widget, "parent") else None
        return (0, 0, 0, 255)

    def _push_undo(self, stroke: Stroke) -> None:
        self._undo_stack.append(stroke)
        if len(self._undo_stack) > UNDO_LIMIT:
            self._undo_stack.pop(0)
        self._redo_stack.clear()


# ------------------------------------------------------------------
# Module-level helpers (pure functions, no Qt state)
# ------------------------------------------------------------------

def _to_qcolor(rgba: RGBA) -> QColor:
    r, g, b, a = rgba
    return QColor(r, g, b, a)


def _build_checker_pixmap(w: int, h: int) -> QPixmap:
    total_w = w * CELL_SIZE
    total_h = h * CELL_SIZE
    pixmap = QPixmap(total_w, total_h)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    for row in range(total_h // CHECKER_CELL + 1):
        for col in range(total_w // CHECKER_CELL + 1):
            color = CHECKER_A if (row + col) % 2 == 0 else CHECKER_B
            painter.fillRect(col * CHECKER_CELL, row * CHECKER_CELL, CHECKER_CELL, CHECKER_CELL, color)
    painter.end()
    return pixmap


def _build_grid_pixmap(w: int, h: int) -> QPixmap:
    total_w = w * CELL_SIZE
    total_h = h * CELL_SIZE
    pixmap = QPixmap(total_w, total_h)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    pen = QPen(GRID_COLOR, 0.5)
    painter.setPen(pen)
    for x in range(w + 1):
        painter.drawLine(x * CELL_SIZE, 0, x * CELL_SIZE, total_h)
    for y in range(h + 1):
        painter.drawLine(0, y * CELL_SIZE, total_w, y * CELL_SIZE)
    painter.end()
    return pixmap
