"""Widget tests for ToolSelectorWidget."""

import pytest
from PySide6.QtCore import Qt

from minecraft_art_gen.editor.tool_selector import ToolSelectorWidget
from minecraft_art_gen.editor.tools import ToolType


@pytest.fixture
def selector(qtbot):
    w = ToolSelectorWidget()
    qtbot.addWidget(w)
    w.show()
    return w


class TestToolSelectorDefaults:
    def test_default_tool_is_pen(self, selector):
        assert selector.current_tool == ToolType.PEN

    def test_pen_button_checked_by_default(self, selector):
        assert selector._pen_btn.isChecked()
        assert not selector._eraser_btn.isChecked()


class TestToolSelectorInteraction:
    def test_clicking_eraser_emits_signal(self, selector, qtbot):
        emitted = []
        selector.tool_changed.connect(emitted.append)
        qtbot.mouseClick(selector._eraser_btn, Qt.MouseButton.LeftButton)
        assert emitted == [ToolType.ERASER]

    def test_clicking_pen_after_eraser_emits_pen(self, selector, qtbot):
        qtbot.mouseClick(selector._eraser_btn, Qt.MouseButton.LeftButton)
        emitted = []
        selector.tool_changed.connect(emitted.append)
        qtbot.mouseClick(selector._pen_btn, Qt.MouseButton.LeftButton)
        assert emitted == [ToolType.PEN]

    def test_clicking_already_selected_does_not_emit(self, selector, qtbot):
        emitted = []
        selector.tool_changed.connect(emitted.append)
        qtbot.mouseClick(selector._pen_btn, Qt.MouseButton.LeftButton)
        assert emitted == []


class TestSetTool:
    def test_set_tool_changes_current_tool(self, selector):
        selector.set_tool(ToolType.ERASER)
        assert selector.current_tool == ToolType.ERASER

    def test_set_tool_updates_button_state(self, selector):
        selector.set_tool(ToolType.ERASER)
        assert selector._eraser_btn.isChecked()
        assert not selector._pen_btn.isChecked()

    def test_set_tool_emits_signal(self, selector):
        emitted = []
        selector.tool_changed.connect(emitted.append)
        selector.set_tool(ToolType.ERASER)
        assert emitted == [ToolType.ERASER]

    def test_set_tool_same_value_does_not_emit(self, selector):
        emitted = []
        selector.tool_changed.connect(emitted.append)
        selector.set_tool(ToolType.PEN)
        assert emitted == []
