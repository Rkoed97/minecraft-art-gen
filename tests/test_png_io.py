"""Tests for PNG I/O round-trips."""

import os
import pytest

from src.models.pixel_image import PixelImage
from src.io.png_reader import load_png
from src.io.png_writer import save_png


RED = (255, 0, 0, 255)
TRANSPARENT = (0, 0, 0, 0)
SEMI = (100, 150, 200, 128)


class TestSavePng:
    def test_creates_file(self, tmp_dir):
        path = os.path.join(tmp_dir, "out.png")
        img = PixelImage(4, 4, fill=RED)
        save_png(img, path)
        assert os.path.exists(path)

    def test_invalid_extension_raises(self, tmp_dir):
        path = os.path.join(tmp_dir, "out.bmp")
        with pytest.raises(ValueError, match=".png"):
            save_png(PixelImage(4, 4), path)

    def test_nonexistent_directory_raises(self):
        with pytest.raises(ValueError):
            save_png(PixelImage(4, 4), "/nonexistent_dir/out.png")


class TestLoadPng:
    def test_load_nonexistent_raises(self, tmp_dir):
        with pytest.raises(ValueError):
            load_png(os.path.join(tmp_dir, "missing.png"))

    def test_load_wrong_extension_raises(self, tmp_dir):
        path = os.path.join(tmp_dir, "file.bmp")
        open(path, "w").close()
        with pytest.raises(ValueError, match=".png"):
            load_png(path)

    def test_load_invalid_image_raises(self, tmp_dir):
        path = os.path.join(tmp_dir, "bad.png")
        with open(path, "wb") as f:
            f.write(b"not an image")
        with pytest.raises(ValueError, match="valid image"):
            load_png(path)


class TestSavePngAtomicWrite:
    def test_cleanup_on_save_error(self, tmp_dir, monkeypatch):
        """Temp file is cleaned up when save fails mid-write."""
        import os
        import glob as g
        from src.io.png_writer import save_png

        original_replace = os.replace

        def failing_replace(src, dst):
            raise OSError("simulated failure")

        monkeypatch.setattr(os, "replace", failing_replace)
        path = os.path.join(tmp_dir, "out.png")
        with pytest.raises(OSError):
            save_png(PixelImage(2, 2), path)
        # No leftover tmp files
        tmp_files = g.glob(os.path.join(tmp_dir, "*.png.tmp"))
        assert tmp_files == []


class TestRoundTrip:
    def test_opaque_pixels_preserved(self, tmp_dir):
        path = os.path.join(tmp_dir, "test.png")
        original = PixelImage(4, 4, fill=RED)
        save_png(original, path)
        loaded = load_png(path)
        assert loaded == original

    def test_transparent_pixels_preserved(self, tmp_dir):
        path = os.path.join(tmp_dir, "test.png")
        original = PixelImage(4, 4)  # all transparent
        save_png(original, path)
        loaded = load_png(path)
        assert loaded == original

    def test_mixed_rgba_preserved(self, tmp_dir):
        path = os.path.join(tmp_dir, "test.png")
        original = (
            PixelImage(3, 3)
            .set_pixel(0, 0, RED)
            .set_pixel(1, 1, SEMI)
            .set_pixel(2, 2, TRANSPARENT)
        )
        save_png(original, path)
        loaded = load_png(path)
        assert loaded == original

    def test_dimensions_preserved(self, tmp_dir):
        path = os.path.join(tmp_dir, "test.png")
        original = PixelImage(16, 32)
        save_png(original, path)
        loaded = load_png(path)
        assert loaded.size == (16, 32)

    def test_large_image_round_trip(self, tmp_dir):
        path = os.path.join(tmp_dir, "large.png")
        original = PixelImage(64, 64, fill=SEMI)
        save_png(original, path)
        loaded = load_png(path)
        assert loaded == original
