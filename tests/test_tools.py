"""Tests for PaintTool and EraseTool."""

import pytest
from minecraft_art_gen.models.pixel_image import PixelImage, TRANSPARENT
from minecraft_art_gen.editor.tools import PaintTool, EraseTool, Stroke

RED = (255, 0, 0, 255)
GREEN = (0, 255, 0, 255)
BLUE = (0, 0, 255, 255)


class TestStroke:
    def test_empty_by_default(self):
        s = Stroke()
        assert s.is_empty

    def test_record_makes_non_empty(self):
        s = Stroke()
        s.record(0, 0, TRANSPARENT, RED)
        assert not s.is_empty

    def test_apply_sets_pixels(self):
        img = PixelImage(3, 3)
        s = Stroke()
        s.record(0, 0, TRANSPARENT, RED)
        s.record(1, 1, TRANSPARENT, GREEN)
        result = s.apply(img)
        assert result.get_pixel(0, 0) == RED
        assert result.get_pixel(1, 1) == GREEN
        assert result.get_pixel(2, 2) == TRANSPARENT

    def test_revert_restores_pixels(self):
        img = PixelImage(3, 3, fill=RED)
        s = Stroke()
        s.record(0, 0, RED, GREEN)
        s.record(1, 1, RED, BLUE)
        painted = s.apply(img)
        assert painted.get_pixel(0, 0) == GREEN
        reverted = s.revert(painted)
        assert reverted.get_pixel(0, 0) == RED
        assert reverted.get_pixel(1, 1) == RED

    def test_first_old_color_wins_for_same_pixel(self):
        """If the same pixel is painted twice in a stroke, the original old_color is kept."""
        s = Stroke()
        s.record(0, 0, TRANSPARENT, RED)
        s.record(0, 0, RED, GREEN)  # second paint on same pixel
        # After revert should go back to TRANSPARENT, not RED
        img = PixelImage(2, 2, fill=GREEN)
        reverted = s.revert(img)
        assert reverted.get_pixel(0, 0) == TRANSPARENT


class TestPaintTool:
    def test_begin_paints_pixel(self):
        tool = PaintTool()
        img = PixelImage(4, 4)
        result = tool.begin(img, 1, 1, RED)
        assert result.get_pixel(1, 1) == RED

    def test_drag_continues_stroke(self):
        tool = PaintTool()
        img = PixelImage(4, 4)
        img = tool.begin(img, 0, 0, RED)
        img = tool.drag(img, 1, 0, RED)
        img = tool.drag(img, 2, 0, RED)
        assert img.get_pixel(0, 0) == RED
        assert img.get_pixel(1, 0) == RED
        assert img.get_pixel(2, 0) == RED

    def test_end_returns_stroke(self):
        tool = PaintTool()
        img = PixelImage(4, 4)
        tool.begin(img, 0, 0, RED)
        stroke = tool.end()
        assert stroke is not None
        assert not stroke.is_empty

    def test_end_without_begin_returns_none(self):
        tool = PaintTool()
        assert tool.end() is None

    def test_out_of_bounds_is_ignored(self):
        tool = PaintTool()
        img = PixelImage(4, 4)
        result = tool.begin(img, 10, 10, RED)
        assert result == img

    def test_painting_same_color_no_stroke(self):
        tool = PaintTool()
        img = PixelImage(4, 4, fill=RED)
        tool.begin(img, 0, 0, RED)
        stroke = tool.end()
        assert stroke is None

    def test_original_image_unchanged(self):
        tool = PaintTool()
        original = PixelImage(4, 4)
        tool.begin(original, 0, 0, RED)
        assert original.get_pixel(0, 0) == TRANSPARENT


class TestEraseTool:
    def test_begin_erases_pixel(self):
        tool = EraseTool()
        img = PixelImage(4, 4, fill=RED)
        result = tool.begin(img, 1, 1)
        assert result.get_pixel(1, 1) == TRANSPARENT
        assert result.get_pixel(0, 0) == RED

    def test_drag_erases_multiple(self):
        tool = EraseTool()
        img = PixelImage(4, 4, fill=RED)
        img = tool.begin(img, 0, 0)
        img = tool.drag(img, 1, 0)
        assert img.get_pixel(0, 0) == TRANSPARENT
        assert img.get_pixel(1, 0) == TRANSPARENT
        assert img.get_pixel(2, 0) == RED

    def test_end_returns_stroke(self):
        tool = EraseTool()
        img = PixelImage(4, 4, fill=RED)
        tool.begin(img, 0, 0)
        stroke = tool.end()
        assert stroke is not None
        assert not stroke.is_empty

    def test_erasing_transparent_no_stroke(self):
        tool = EraseTool()
        img = PixelImage(4, 4)  # all transparent
        tool.begin(img, 0, 0)
        stroke = tool.end()
        assert stroke is None

    def test_out_of_bounds_is_ignored(self):
        tool = EraseTool()
        img = PixelImage(4, 4, fill=RED)
        result = tool.begin(img, 10, 10)
        assert result == img


class TestUndoRedo:
    def test_stroke_revert_round_trip(self):
        tool = PaintTool()
        img = PixelImage(4, 4)
        painted = tool.begin(img, 0, 0, RED)
        painted = tool.drag(painted, 1, 0, RED)
        stroke = tool.end()
        assert stroke is not None
        reverted = stroke.revert(painted)
        assert reverted.get_pixel(0, 0) == TRANSPARENT
        assert reverted.get_pixel(1, 0) == TRANSPARENT

    def test_erase_stroke_revert_round_trip(self):
        tool = EraseTool()
        img = PixelImage(4, 4, fill=RED)
        erased = tool.begin(img, 0, 0)
        stroke = tool.end()
        assert stroke is not None
        reverted = stroke.revert(erased)
        assert reverted.get_pixel(0, 0) == RED
