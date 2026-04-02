"""Integration tests: full workflow from canvas creation through save/load round-trip.

These tests exercise the complete data pipeline:
  asset type selection -> new PixelImage -> paint/erase -> save_png -> load_png -> verify
"""

import os
import pytest

from src.models.asset_type import ASSET_TYPES
from src.models.pixel_image import PixelImage, TRANSPARENT
from src.editor.tools import PaintTool, EraseTool
from src.io.png_writer import save_png
from src.io.png_reader import load_png

RED = (255, 0, 0, 255)
GREEN = (0, 255, 0, 255)
BLUE = (0, 0, 255, 200)   # semi-transparent
SEMI = (128, 64, 32, 128)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def paint_stroke(image: PixelImage, coords: list[tuple[int, int]], color) -> tuple[PixelImage, object]:
    """Apply a paint stroke and return (new_image, stroke) for undo testing."""
    tool = PaintTool()
    x0, y0 = coords[0]
    image = tool.begin(image, x0, y0, color)
    for x, y in coords[1:]:
        image = tool.drag(image, x, y, color)
    stroke = tool.end()
    return image, stroke


def erase_stroke(image: PixelImage, coords: list[tuple[int, int]]) -> tuple[PixelImage, object]:
    tool = EraseTool()
    x0, y0 = coords[0]
    image = tool.begin(image, x0, y0)
    for x, y in coords[1:]:
        image = tool.drag(image, x, y)
    stroke = tool.end()
    return image, stroke


def round_trip(image: PixelImage, path: str) -> PixelImage:
    """Save to disk and reload — returns the reloaded image."""
    save_png(image, path)
    return load_png(path)


# ---------------------------------------------------------------------------
# Asset type round-trips
# ---------------------------------------------------------------------------

class TestAssetTypeRoundTrips:
    """Each test simulates: create image at correct size -> paint some pixels -> save -> reload -> verify."""

    def test_block_16x16_round_trip(self, tmp_dir):
        at = ASSET_TYPES["block"]
        w, h = at.default_size
        img = PixelImage(w, h)
        img, _ = paint_stroke(img, [(0, 0), (1, 0), (2, 0)], RED)
        img, _ = paint_stroke(img, [(3, 3)], SEMI)
        path = os.path.join(tmp_dir, "block.png")
        loaded = round_trip(img, path)
        assert loaded == img
        assert loaded.size == (w, h)

    def test_block_32x32_higher_res(self, tmp_dir):
        img = PixelImage(32, 32)
        img, _ = paint_stroke(img, [(0, 0), (31, 31)], BLUE)
        path = os.path.join(tmp_dir, "block_32.png")
        loaded = round_trip(img, path)
        assert loaded == img

    def test_block_256x256_highest_res(self, tmp_dir):
        img = PixelImage(256, 256)
        img, _ = paint_stroke(img, [(0, 0), (255, 255), (128, 128)], GREEN)
        path = os.path.join(tmp_dir, "block_256.png")
        loaded = round_trip(img, path)
        assert loaded == img

    def test_item_16x16_round_trip(self, tmp_dir):
        at = ASSET_TYPES["item"]
        w, h = at.default_size
        img = PixelImage(w, h)
        # Paint a simple sword silhouette-like pattern
        for i in range(w):
            img, _ = paint_stroke(img, [(i, i % h)], RED)
        path = os.path.join(tmp_dir, "item.png")
        loaded = round_trip(img, path)
        assert loaded == img

    def test_item_128x128_higher_res(self, tmp_dir):
        img = PixelImage(128, 128)
        img, _ = paint_stroke(img, [(64, 64)], SEMI)
        path = os.path.join(tmp_dir, "item_128.png")
        loaded = round_trip(img, path)
        assert loaded == img

    def test_entity_classic_64x32(self, tmp_dir):
        at = ASSET_TYPES["entity_classic"]
        w, h = at.default_size
        assert (w, h) == (64, 32)
        img = PixelImage(w, h)
        img, _ = paint_stroke(img, [(0, 0), (63, 31)], GREEN)
        path = os.path.join(tmp_dir, "entity_classic.png")
        loaded = round_trip(img, path)
        assert loaded == img

    def test_entity_humanoid_64x64(self, tmp_dir):
        at = ASSET_TYPES["entity_humanoid"]
        w, h = at.default_size
        assert (w, h) == (64, 64)
        img = PixelImage(w, h)
        img, _ = paint_stroke(img, [(8, 8), (56, 56)], BLUE)
        path = os.path.join(tmp_dir, "entity_human.png")
        loaded = round_trip(img, path)
        assert loaded == img

    def test_gui_256x256(self, tmp_dir):
        at = ASSET_TYPES["gui"]
        w, h = at.default_size
        img = PixelImage(w, h)
        img, _ = paint_stroke(img, [(0, 0), (255, 255)], RED)
        path = os.path.join(tmp_dir, "gui.png")
        loaded = round_trip(img, path)
        assert loaded == img

    def test_effect_icon_18x18(self, tmp_dir):
        at = ASSET_TYPES["effect_icon"]
        w, h = at.default_size
        assert (w, h) == (18, 18)
        img = PixelImage(w, h)
        img, _ = paint_stroke(img, [(9, 9)], SEMI)
        path = os.path.join(tmp_dir, "effect.png")
        loaded = round_trip(img, path)
        assert loaded == img

    def test_painting_grand_64x64(self, tmp_dir):
        at = ASSET_TYPES["painting_grand"]
        w, h = at.default_size
        img = PixelImage(w, h, fill=BLUE)
        img, _ = paint_stroke(img, [(32, 32)], RED)
        path = os.path.join(tmp_dir, "painting_grand.png")
        loaded = round_trip(img, path)
        assert loaded == img

    def test_particle_8x8(self, tmp_dir):
        at = ASSET_TYPES["particle"]
        w, h = at.default_size
        assert (w, h) == (8, 8)
        img = PixelImage(w, h)
        for x in range(w):
            for y in range(h):
                img, _ = paint_stroke(img, [(x, y)], (x * 30, y * 30, 128, 200))
        path = os.path.join(tmp_dir, "particle.png")
        loaded = round_trip(img, path)
        assert loaded == img

    def test_trim_16x32(self, tmp_dir):
        at = ASSET_TYPES["trim"]
        w, h = at.default_size
        assert (w, h) == (16, 32)
        img = PixelImage(w, h)
        img, _ = paint_stroke(img, [(0, 0), (15, 31)], GREEN)
        path = os.path.join(tmp_dir, "trim.png")
        loaded = round_trip(img, path)
        assert loaded == img

    def test_trim_64x128_higher_res(self, tmp_dir):
        img = PixelImage(64, 128)
        img, _ = paint_stroke(img, [(32, 64)], SEMI)
        path = os.path.join(tmp_dir, "trim_64.png")
        loaded = round_trip(img, path)
        assert loaded == img


# ---------------------------------------------------------------------------
# Transparency round-trips
# ---------------------------------------------------------------------------

class TestTransparencyRoundTrips:
    def test_fully_transparent_image(self, tmp_dir):
        img = PixelImage(16, 16)  # all transparent
        path = os.path.join(tmp_dir, "transparent.png")
        loaded = round_trip(img, path)
        for y in range(16):
            for x in range(16):
                assert loaded.get_pixel(x, y) == TRANSPARENT

    def test_mixed_alpha_preserved(self, tmp_dir):
        img = PixelImage(4, 4)
        colors = [
            (255, 0, 0, 255),    # fully opaque
            (0, 255, 0, 128),    # semi-transparent
            (0, 0, 255, 1),      # almost transparent
            (100, 100, 100, 0),  # fully transparent
        ]
        for i, color in enumerate(colors):
            img, _ = paint_stroke(img, [(i, 0)], color)
        path = os.path.join(tmp_dir, "alpha.png")
        loaded = round_trip(img, path)
        for i, color in enumerate(colors):
            assert loaded.get_pixel(i, 0) == color

    def test_erase_then_save_transparent(self, tmp_dir):
        img = PixelImage(8, 8, fill=RED)
        img, _ = erase_stroke(img, [(0, 0), (1, 0), (2, 0)])
        path = os.path.join(tmp_dir, "erased.png")
        loaded = round_trip(img, path)
        assert loaded.get_pixel(0, 0) == TRANSPARENT
        assert loaded.get_pixel(1, 0) == TRANSPARENT
        assert loaded.get_pixel(2, 0) == TRANSPARENT
        assert loaded.get_pixel(3, 0) == RED


# ---------------------------------------------------------------------------
# Undo/Redo workflow
# ---------------------------------------------------------------------------

class TestUndoRedoWorkflow:
    def test_undo_then_save_reflects_reverted_state(self, tmp_dir):
        img = PixelImage(4, 4)
        img, stroke = paint_stroke(img, [(0, 0)], RED)
        assert img.get_pixel(0, 0) == RED

        # Undo the stroke
        reverted = stroke.revert(img)
        assert reverted.get_pixel(0, 0) == TRANSPARENT

        path = os.path.join(tmp_dir, "undo_save.png")
        loaded = round_trip(reverted, path)
        assert loaded.get_pixel(0, 0) == TRANSPARENT

    def test_redo_then_save_reflects_reapplied_state(self, tmp_dir):
        img = PixelImage(4, 4)
        img, stroke = paint_stroke(img, [(1, 1)], GREEN)
        reverted = stroke.revert(img)
        reapplied = stroke.apply(reverted)
        assert reapplied.get_pixel(1, 1) == GREEN

        path = os.path.join(tmp_dir, "redo_save.png")
        loaded = round_trip(reapplied, path)
        assert loaded.get_pixel(1, 1) == GREEN

    def test_multiple_stroke_undo_sequence(self, tmp_dir):
        img = PixelImage(8, 8)
        img, stroke1 = paint_stroke(img, [(0, 0)], RED)
        img, stroke2 = paint_stroke(img, [(1, 1)], GREEN)
        img, stroke3 = paint_stroke(img, [(2, 2)], BLUE)

        # Undo stroke3, stroke2 — only stroke1 remains
        img = stroke3.revert(img)
        img = stroke2.revert(img)

        assert img.get_pixel(0, 0) == RED
        assert img.get_pixel(1, 1) == TRANSPARENT
        assert img.get_pixel(2, 2) == TRANSPARENT

        path = os.path.join(tmp_dir, "multi_undo.png")
        loaded = round_trip(img, path)
        assert loaded == img


# ---------------------------------------------------------------------------
# Resize workflow
# ---------------------------------------------------------------------------

class TestResizeWorkflow:
    def test_grow_then_save(self, tmp_dir):
        img = PixelImage(16, 16, fill=RED)
        bigger = img.resize(32, 32)
        path = os.path.join(tmp_dir, "grown.png")
        loaded = round_trip(bigger, path)
        assert loaded.size == (32, 32)
        # Original region preserved
        assert loaded.get_pixel(0, 0) == RED
        assert loaded.get_pixel(15, 15) == RED
        # New region is transparent
        assert loaded.get_pixel(16, 16) == TRANSPARENT
        assert loaded.get_pixel(31, 31) == TRANSPARENT

    def test_shrink_then_save(self, tmp_dir):
        img = PixelImage(32, 32, fill=GREEN)
        smaller = img.resize(16, 16)
        path = os.path.join(tmp_dir, "shrunk.png")
        loaded = round_trip(smaller, path)
        assert loaded.size == (16, 16)
        assert loaded.get_pixel(0, 0) == GREEN
        assert loaded.get_pixel(15, 15) == GREEN

    def test_paint_after_resize(self, tmp_dir):
        img = PixelImage(8, 8)
        img = img.resize(16, 16)
        img, _ = paint_stroke(img, [(10, 10)], RED)
        path = os.path.join(tmp_dir, "paint_after_resize.png")
        loaded = round_trip(img, path)
        assert loaded.get_pixel(10, 10) == RED
        assert loaded.size == (16, 16)


# ---------------------------------------------------------------------------
# Full end-to-end workflow simulation
# ---------------------------------------------------------------------------

class TestFullWorkflow:
    def test_create_paint_save_open_edit_save(self, tmp_dir):
        """Simulate: new file -> paint -> save -> reopen -> paint more -> save again."""
        path = os.path.join(tmp_dir, "workflow.png")

        # Session 1: create and paint
        img = PixelImage(16, 16)
        img, _ = paint_stroke(img, [(0, 0), (1, 0), (2, 0)], RED)
        img, _ = paint_stroke(img, [(0, 1), (1, 1)], GREEN)
        save_png(img, path)

        # Session 2: open, verify, paint more, save
        img2 = load_png(path)
        assert img2.get_pixel(0, 0) == RED
        assert img2.get_pixel(0, 1) == GREEN
        assert img2.get_pixel(15, 15) == TRANSPARENT

        img2, _ = paint_stroke(img2, [(15, 15)], BLUE)
        save_png(img2, path)

        # Session 3: verify final state
        img3 = load_png(path)
        assert img3.get_pixel(0, 0) == RED
        assert img3.get_pixel(0, 1) == GREEN
        assert img3.get_pixel(15, 15) == BLUE

    def test_all_asset_types_can_be_created_and_saved(self, tmp_dir):
        """Smoke test: every asset type in the registry can produce a valid PNG."""
        from src.models.asset_type import ASSET_TYPES, ASSET_TYPE_ORDER
        for key in ASSET_TYPE_ORDER:
            at = ASSET_TYPES[key]
            w, h = at.default_size
            img = PixelImage(w, h)
            img, _ = paint_stroke(img, [(0, 0)], RED)
            path = os.path.join(tmp_dir, f"{key}.png")
            save_png(img, path)
            loaded = load_png(path)
            assert loaded.size == (w, h), f"{key}: size mismatch"
            assert loaded.get_pixel(0, 0) == RED, f"{key}: pixel mismatch"

    def test_overwrite_existing_file(self, tmp_dir):
        """Saving to an existing path replaces it correctly (atomic write)."""
        path = os.path.join(tmp_dir, "overwrite.png")
        img1 = PixelImage(8, 8, fill=RED)
        save_png(img1, path)

        img2 = PixelImage(8, 8, fill=GREEN)
        save_png(img2, path)

        loaded = load_png(path)
        assert loaded == img2

    def test_project_folder_isolation(self, tmp_path):
        """Multiple project folders can each have their own files independently."""
        folder_a = tmp_path / "project_a"
        folder_b = tmp_path / "project_b"
        folder_a.mkdir()
        folder_b.mkdir()

        img_a = PixelImage(16, 16, fill=RED)
        img_b = PixelImage(16, 16, fill=GREEN)

        path_a = str(folder_a / "block.png")
        path_b = str(folder_b / "block.png")

        save_png(img_a, path_a)
        save_png(img_b, path_b)

        loaded_a = load_png(path_a)
        loaded_b = load_png(path_b)

        assert loaded_a == img_a
        assert loaded_b == img_b
        assert loaded_a != loaded_b
