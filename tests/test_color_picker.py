"""Widget tests for RgbaSliderRow and ColorPickerWidget."""

import pytest
from PySide6.QtCore import Qt

from minecraft_art_gen.editor.color_picker import RgbaSliderRow, ColorPickerWidget


@pytest.fixture
def slider_row(qtbot):
    w = RgbaSliderRow("R")
    qtbot.addWidget(w)
    w.show()
    return w


@pytest.fixture
def picker(qtbot):
    w = ColorPickerWidget()
    qtbot.addWidget(w)
    w.show()
    return w


class TestRgbaSliderRow:
    def test_initial_value_is_zero(self, slider_row):
        assert slider_row.value() == 0

    def test_set_value_updates_slider_and_spinbox(self, slider_row):
        slider_row.set_value(128)
        assert slider_row._slider.value() == 128
        assert slider_row._spinbox.value() == 128

    def test_set_value_does_not_emit_signal(self, slider_row):
        emitted = []
        slider_row.value_changed.connect(emitted.append)
        slider_row.set_value(200)
        assert emitted == []

    def test_slider_change_emits_signal(self, slider_row):
        emitted = []
        slider_row.value_changed.connect(emitted.append)
        slider_row._slider.setValue(100)
        assert emitted == [100]

    def test_slider_change_syncs_spinbox(self, slider_row):
        slider_row._slider.setValue(75)
        assert slider_row._spinbox.value() == 75

    def test_spinbox_change_emits_signal(self, slider_row):
        emitted = []
        slider_row.value_changed.connect(emitted.append)
        slider_row._spinbox.setValue(200)
        assert emitted == [200]

    def test_spinbox_change_syncs_slider(self, slider_row):
        slider_row._spinbox.setValue(42)
        assert slider_row._slider.value() == 42

    def test_slider_change_does_not_double_emit(self, slider_row):
        emitted = []
        slider_row.value_changed.connect(emitted.append)
        slider_row._slider.setValue(50)
        assert len(emitted) == 1

    def test_spinbox_change_does_not_double_emit(self, slider_row):
        emitted = []
        slider_row.value_changed.connect(emitted.append)
        slider_row._spinbox.setValue(50)
        assert len(emitted) == 1

    def test_range_clamped_to_255(self, slider_row):
        slider_row._spinbox.setValue(300)
        assert slider_row.value() == 255


class TestColorPickerWidget:
    def test_default_color_is_black_opaque(self, picker):
        assert picker.current_color == (0, 0, 0, 255)

    def test_sliders_reflect_default_color(self, picker):
        assert picker._r_row.value() == 0
        assert picker._g_row.value() == 0
        assert picker._b_row.value() == 0
        assert picker._a_row.value() == 255

    def test_moving_r_slider_updates_color(self, picker):
        emitted = []
        picker.color_changed.connect(emitted.append)
        picker._r_row._slider.setValue(128)
        assert picker.current_color[0] == 128
        assert len(emitted) == 1

    def test_moving_a_slider_updates_alpha(self, picker):
        picker._a_row._slider.setValue(0)
        assert picker.current_color[3] == 0

    def test_moving_slider_updates_hex_edit(self, picker):
        picker._r_row._slider.setValue(255)
        assert picker._hex_edit.text().startswith("ff")

    def test_apply_color_updates_all_sliders(self, picker):
        picker._apply_color((10, 20, 30, 40))
        assert picker._r_row.value() == 10
        assert picker._g_row.value() == 20
        assert picker._b_row.value() == 30
        assert picker._a_row.value() == 40

    def test_apply_color_updates_hex(self, picker):
        picker._apply_color((255, 0, 0, 255))
        assert picker._hex_edit.text() == "ff0000ff"

    def test_channel_change_does_not_double_emit(self, picker):
        emitted = []
        picker.color_changed.connect(emitted.append)
        picker._r_row._slider.setValue(100)
        assert len(emitted) == 1
