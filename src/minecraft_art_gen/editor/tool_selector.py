"""Tool selector widget: toggle between Pen and Eraser."""

from PySide6.QtWidgets import QGroupBox, QVBoxLayout, QPushButton, QButtonGroup
from PySide6.QtCore import Signal

from minecraft_art_gen.editor.tools import ToolType


class ToolSelectorWidget(QGroupBox):
    tool_changed = Signal(object)  # emits ToolType

    def __init__(self, parent=None) -> None:
        super().__init__("Tools", parent)
        self._current_tool = ToolType.PEN

        layout = QVBoxLayout(self)
        layout.setSpacing(4)

        self._pen_btn = QPushButton("Pen  [P]")
        self._pen_btn.setCheckable(True)
        self._pen_btn.setChecked(True)
        self._pen_btn.setToolTip("Draw pixels (P)")

        self._eraser_btn = QPushButton("Eraser  [E]")
        self._eraser_btn.setCheckable(True)
        self._eraser_btn.setToolTip("Erase pixels (E)")

        self._group = QButtonGroup(self)
        self._group.setExclusive(True)
        self._group.addButton(self._pen_btn, 0)
        self._group.addButton(self._eraser_btn, 1)

        layout.addWidget(self._pen_btn)
        layout.addWidget(self._eraser_btn)

        self._group.idClicked.connect(self._on_button_clicked)

    @property
    def current_tool(self) -> ToolType:
        return self._current_tool

    def set_tool(self, tool: ToolType) -> None:
        if tool == self._current_tool:
            return
        self._current_tool = tool
        self._pen_btn.setChecked(tool == ToolType.PEN)
        self._eraser_btn.setChecked(tool == ToolType.ERASER)
        self.tool_changed.emit(tool)

    def _on_button_clicked(self, button_id: int) -> None:
        tool = ToolType.PEN if button_id == 0 else ToolType.ERASER
        if tool == self._current_tool:
            return
        self._current_tool = tool
        self.tool_changed.emit(tool)
