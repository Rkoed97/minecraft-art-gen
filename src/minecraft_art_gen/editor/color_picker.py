"""RGBA color picker widget."""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit,
    QGroupBox,
)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QColor, QPainter, QBrush


RGBA = tuple[int, int, int, int]
_DEFAULT_COLOR: RGBA = (0, 0, 0, 255)


class ColorSwatchWidget(QWidget):
    """A small rectangle showing the current color over a checkerboard (for alpha vis)."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setFixedSize(48, 48)
        self._color: RGBA = _DEFAULT_COLOR

    def set_color(self, color: RGBA) -> None:
        self._color = color
        self.update()

    def paintEvent(self, _event) -> None:
        painter = QPainter(self)
        # Checkerboard background for transparency visibility
        cell = 8
        for row in range(self.height() // cell + 1):
            for col in range(self.width() // cell + 1):
                if (row + col) % 2 == 0:
                    painter.fillRect(col * cell, row * cell, cell, cell, QColor(200, 200, 200))
                else:
                    painter.fillRect(col * cell, row * cell, cell, cell, QColor(150, 150, 150))
        # Color overlay
        r, g, b, a = self._color
        painter.fillRect(0, 0, self.width(), self.height(), QColor(r, g, b, a))
        painter.end()


class ColorPickerWidget(QGroupBox):
    color_changed = Signal(tuple)  # emits (r, g, b, a)

    def __init__(self, parent=None) -> None:
        super().__init__("Color", parent)
        self._color: RGBA = _DEFAULT_COLOR
        self._build_ui()

    @property
    def current_color(self) -> RGBA:
        return self._color

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setSpacing(8)

        # Swatch + pick button
        swatch_row = QHBoxLayout()
        self._swatch = ColorSwatchWidget()
        swatch_row.addWidget(self._swatch)
        pick_btn = QPushButton("Pick Color…")
        pick_btn.clicked.connect(self._open_dialog)
        swatch_row.addWidget(pick_btn)
        root.addLayout(swatch_row)

        # Hex input
        hex_row = QHBoxLayout()
        hex_row.addWidget(QLabel("Hex:"))
        self._hex_edit = QLineEdit()
        self._hex_edit.setPlaceholderText("RRGGBBAA")
        self._hex_edit.setMaxLength(8)
        self._hex_edit.editingFinished.connect(self._apply_hex)
        hex_row.addWidget(self._hex_edit)
        root.addLayout(hex_row)

        # RGBA labels
        self._rgba_label = QLabel()
        self._rgba_label.setStyleSheet("font-size: 10px; color: gray;")
        root.addWidget(self._rgba_label)

        self._apply_color(_DEFAULT_COLOR)

    def _open_dialog(self) -> None:
        from PySide6.QtWidgets import QColorDialog
        r, g, b, a = self._color
        initial = QColor(r, g, b, a)
        dialog = QColorDialog(initial, self)
        dialog.setOption(QColorDialog.ColorDialogOption.ShowAlphaChannel, True)
        if dialog.exec():
            qc = dialog.selectedColor()
            self._apply_color((qc.red(), qc.green(), qc.blue(), qc.alpha()))

    def _apply_hex(self) -> None:
        text = self._hex_edit.text().strip().lstrip("#")
        if len(text) == 6:
            text += "ff"
        if len(text) != 8:
            self._hex_edit.setText(_rgba_to_hex(self._color))
            return
        try:
            r = int(text[0:2], 16)
            g = int(text[2:4], 16)
            b = int(text[4:6], 16)
            a = int(text[6:8], 16)
        except ValueError:
            self._hex_edit.setText(_rgba_to_hex(self._color))
            return
        self._apply_color((r, g, b, a))

    def _apply_color(self, color: RGBA) -> None:
        self._color = color
        self._swatch.set_color(color)
        self._hex_edit.setText(_rgba_to_hex(color))
        r, g, b, a = color
        self._rgba_label.setText(f"R:{r}  G:{g}  B:{b}  A:{a}")
        self.color_changed.emit(color)


def _rgba_to_hex(color: RGBA) -> str:
    r, g, b, a = color
    return f"{r:02x}{g:02x}{b:02x}{a:02x}"
