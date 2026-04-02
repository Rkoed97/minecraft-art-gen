"""Editor screen — orchestrates canvas, color picker, toolbar, and file I/O."""

import os

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QToolBar, QPushButton,
    QLabel, QSpinBox, QFileDialog, QMessageBox, QSizePolicy, QStatusBar,
    QMainWindow,
)
from PySide6.QtCore import Signal, Qt, QSize
from PySide6.QtGui import QKeySequence, QShortcut

from minecraft_art_gen.models.asset_type import AssetType
from minecraft_art_gen.models.pixel_image import PixelImage


class EditorScreen(QWidget):
    back_requested = Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._project_path: str = ""
        self._file_path: str = ""
        self._pixel_image: PixelImage = PixelImage(16, 16)
        self._dirty: bool = False

        self._build_ui()
        self._setup_shortcuts()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def new_canvas(self, asset_type: AssetType, width: int, height: int, project_path: str) -> None:
        self._project_path = project_path
        self._file_path = ""
        self._pixel_image = PixelImage(width, height)
        self._dirty = False
        self._canvas.set_image(self._pixel_image)
        self._width_spin.setValue(width)
        self._height_spin.setValue(height)
        self._update_status()

    def load_canvas(self, pixel_image: PixelImage, file_path: str, project_path: str) -> None:
        self._project_path = project_path
        self._file_path = file_path
        self._pixel_image = pixel_image
        self._dirty = False
        self._canvas.set_image(pixel_image)
        self._width_spin.setValue(pixel_image.width)
        self._height_spin.setValue(pixel_image.height)
        self._update_status()

    def is_dirty(self) -> bool:
        return self._dirty

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Top toolbar
        toolbar = self._build_toolbar()
        root.addWidget(toolbar)

        # Main area: left panel + canvas
        main_area = QHBoxLayout()
        main_area.setContentsMargins(8, 8, 8, 8)
        main_area.setSpacing(8)

        left_panel = self._build_left_panel()
        main_area.addWidget(left_panel)

        from minecraft_art_gen.editor.canvas import PixelCanvas
        self._canvas = PixelCanvas()
        self._canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._canvas.pixel_painted.connect(self._on_pixel_painted)
        self._canvas.pixels_changed.connect(self._on_pixels_changed)
        main_area.addWidget(self._canvas)

        root.addLayout(main_area)

        # Status bar
        self._status_bar = self._build_status_bar()
        root.addWidget(self._status_bar)

        self._canvas.cursor_moved.connect(self._on_cursor_moved)
        self._canvas.zoom_changed.connect(self._on_zoom_changed)

    def _build_toolbar(self) -> QWidget:
        bar = QWidget()
        bar.setFixedHeight(40)
        bar.setStyleSheet("background: #2b2b2b;")
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(6)

        back_btn = QPushButton("← Back")
        back_btn.setFixedWidth(70)
        back_btn.clicked.connect(self._on_back)
        layout.addWidget(back_btn)

        layout.addStretch()

        self._file_label = QLabel("New File")
        self._file_label.setStyleSheet("color: #cccccc;")
        layout.addWidget(self._file_label)

        layout.addStretch()

        open_btn = QPushButton("Open…")
        open_btn.setFixedWidth(70)
        open_btn.clicked.connect(self._open_file)
        layout.addWidget(open_btn)

        save_btn = QPushButton("Save")
        save_btn.setFixedWidth(70)
        save_btn.clicked.connect(self._save_file)
        layout.addWidget(save_btn)

        save_as_btn = QPushButton("Save As…")
        save_as_btn.setFixedWidth(80)
        save_as_btn.clicked.connect(self._save_file_as)
        layout.addWidget(save_as_btn)

        return bar

    def _build_left_panel(self) -> QWidget:
        from minecraft_art_gen.editor.color_picker import ColorPickerWidget
        from minecraft_art_gen.editor.tool_selector import ToolSelectorWidget
        panel = QWidget()
        panel.setFixedWidth(200)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        # Tool selector
        self._tool_selector = ToolSelectorWidget()
        self._tool_selector.tool_changed.connect(self._on_tool_changed)
        layout.addWidget(self._tool_selector)

        # Color picker
        self._color_picker = ColorPickerWidget()
        layout.addWidget(self._color_picker)

        # Canvas dimensions
        dim_label = QLabel("Canvas Size")
        dim_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(dim_label)

        dim_row = QHBoxLayout()
        self._width_spin = QSpinBox()
        self._width_spin.setRange(1, 512)
        self._width_spin.setValue(16)
        self._height_spin = QSpinBox()
        self._height_spin.setRange(1, 512)
        self._height_spin.setValue(16)
        dim_row.addWidget(QLabel("W:"))
        dim_row.addWidget(self._width_spin)
        dim_row.addWidget(QLabel("H:"))
        dim_row.addWidget(self._height_spin)
        layout.addLayout(dim_row)

        resize_btn = QPushButton("Resize Canvas")
        resize_btn.clicked.connect(self._resize_canvas)
        layout.addWidget(resize_btn)

        # Undo/Redo
        undo_redo_row = QHBoxLayout()
        undo_btn = QPushButton("Undo")
        undo_btn.clicked.connect(self._undo)
        redo_btn = QPushButton("Redo")
        redo_btn.clicked.connect(self._redo)
        undo_redo_row.addWidget(undo_btn)
        undo_redo_row.addWidget(redo_btn)
        layout.addLayout(undo_redo_row)

        layout.addStretch()
        return panel

    def _build_status_bar(self) -> QWidget:
        bar = QWidget()
        bar.setFixedHeight(24)
        bar.setStyleSheet("background: #1e1e1e; color: #aaaaaa; font-size: 11px;")
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(8, 0, 8, 0)
        layout.setSpacing(16)
        self._cursor_label = QLabel("—")
        self._dims_label = QLabel("16×16")
        self._zoom_label = QLabel("100%")
        self._dirty_label = QLabel("")
        for lbl in (self._cursor_label, self._dims_label, self._zoom_label, self._dirty_label):
            layout.addWidget(lbl)
        layout.addStretch()
        return bar

    def _setup_shortcuts(self) -> None:
        QShortcut(QKeySequence("Ctrl+S"), self).activated.connect(self._save_file)
        QShortcut(QKeySequence("Ctrl+Shift+S"), self).activated.connect(self._save_file_as)
        QShortcut(QKeySequence("Ctrl+O"), self).activated.connect(self._open_file)
        QShortcut(QKeySequence("Ctrl+Z"), self).activated.connect(self._undo)
        QShortcut(QKeySequence("Ctrl+Y"), self).activated.connect(self._redo)
        QShortcut(QKeySequence("Escape"), self).activated.connect(self._on_back)
        QShortcut(QKeySequence("P"), self).activated.connect(self._select_pen)
        QShortcut(QKeySequence("E"), self).activated.connect(self._select_eraser)

    # ------------------------------------------------------------------
    # Undo / Redo (delegated to canvas)
    # ------------------------------------------------------------------

    def _undo(self) -> None:
        result = self._canvas.undo()
        if result is not None:
            self._pixel_image = result
            self._dirty = True
            self._update_status()

    def _redo(self) -> None:
        result = self._canvas.redo()
        if result is not None:
            self._pixel_image = result
            self._dirty = True
            self._update_status()

    # ------------------------------------------------------------------
    # File operations
    # ------------------------------------------------------------------

    def _save_file(self) -> None:
        if not self._file_path:
            self._save_file_as()
            return
        self._do_save(self._file_path)

    def _save_file_as(self) -> None:
        start = self._file_path or self._project_path or ""
        path, _ = QFileDialog.getSaveFileName(self, "Save PNG", start, "PNG Images (*.png)")
        if path:
            if not path.lower().endswith(".png"):
                path += ".png"
            self._do_save(path)

    def _do_save(self, path: str) -> None:
        from minecraft_art_gen.io.png_writer import save_png
        try:
            save_png(self._pixel_image, path)
        except (ValueError, OSError) as exc:
            QMessageBox.critical(self, "Save Failed", str(exc))
            return
        self._file_path = path
        self._dirty = False
        self._update_status()

    def _open_file(self) -> None:
        if self._dirty:
            result = QMessageBox.question(
                self, "Unsaved Changes",
                "Discard current changes and open a file?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if result != QMessageBox.StandardButton.Yes:
                return
        start = self._file_path or self._project_path or ""
        path, _ = QFileDialog.getOpenFileName(self, "Open PNG", start, "PNG Images (*.png)")
        if not path:
            return
        from minecraft_art_gen.io.png_reader import load_png
        try:
            img = load_png(path)
        except (ValueError, OSError) as exc:
            QMessageBox.critical(self, "Open Failed", str(exc))
            return
        self.load_canvas(img, path, self._project_path)

    # ------------------------------------------------------------------
    # Canvas resize
    # ------------------------------------------------------------------

    def _resize_canvas(self) -> None:
        new_w = self._width_spin.value()
        new_h = self._height_spin.value()
        if (new_w, new_h) == self._pixel_image.size:
            return
        if new_w < self._pixel_image.width or new_h < self._pixel_image.height:
            result = QMessageBox.question(
                self, "Resize Canvas",
                f"Shrinking from {self._pixel_image.width}×{self._pixel_image.height} "
                f"to {new_w}×{new_h} will clip content. Continue?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if result != QMessageBox.StandardButton.Yes:
                return
        self._pixel_image = self._pixel_image.resize(new_w, new_h)
        self._canvas.set_image(self._pixel_image)
        self._dirty = True
        self._update_status()

    # ------------------------------------------------------------------
    # Navigation
    # ------------------------------------------------------------------

    def _on_back(self) -> None:
        if self._dirty:
            result = QMessageBox.question(
                self, "Unsaved Changes",
                "You have unsaved changes. Go back anyway?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if result != QMessageBox.StandardButton.Yes:
                return
        self.back_requested.emit()

    # ------------------------------------------------------------------
    # Canvas signal handlers
    # ------------------------------------------------------------------

    def _on_tool_changed(self, tool) -> None:
        self._canvas.set_active_tool(tool)

    def _select_pen(self) -> None:
        from minecraft_art_gen.editor.tools import ToolType
        self._tool_selector.set_tool(ToolType.PEN)

    def _select_eraser(self) -> None:
        from minecraft_art_gen.editor.tools import ToolType
        self._tool_selector.set_tool(ToolType.ERASER)

    def _on_pixel_painted(self, pixel_image: PixelImage) -> None:
        self._pixel_image = pixel_image
        self._dirty = True
        self._update_status()

    def _on_pixels_changed(self, pixel_image: PixelImage) -> None:
        self._pixel_image = pixel_image

    # ------------------------------------------------------------------
    # Status bar
    # ------------------------------------------------------------------

    def _on_cursor_moved(self, x: int, y: int) -> None:
        if x < 0:
            self._cursor_label.setText("—")
        else:
            self._cursor_label.setText(f"({x}, {y})")

    def _on_zoom_changed(self, pct: int) -> None:
        self._zoom_label.setText(f"{pct}%")

    def _update_status(self) -> None:
        w, h = self._pixel_image.size
        self._dims_label.setText(f"{w}×{h}")
        name = os.path.basename(self._file_path) if self._file_path else "New File"
        self._file_label.setText(("* " if self._dirty else "") + name)
        self._dirty_label.setText("● Unsaved" if self._dirty else "")
