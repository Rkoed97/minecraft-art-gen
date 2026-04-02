"""Tests for input validators."""

import os
import pytest

from minecraft_art_gen.utils.validators import (
    validate_dimensions,
    validate_project_path,
    validate_png_path,
    validate_save_path,
    MAX_DIMENSION,
)


class TestValidateDimensions:
    def test_valid(self):
        validate_dimensions(16, 16)
        validate_dimensions(1, 1)
        validate_dimensions(MAX_DIMENSION, MAX_DIMENSION)

    def test_zero_width(self):
        with pytest.raises(ValueError):
            validate_dimensions(0, 16)

    def test_zero_height(self):
        with pytest.raises(ValueError):
            validate_dimensions(16, 0)

    def test_negative(self):
        with pytest.raises(ValueError):
            validate_dimensions(-1, 16)

    def test_exceeds_max(self):
        with pytest.raises(ValueError):
            validate_dimensions(MAX_DIMENSION + 1, 16)

    def test_non_integer(self):
        with pytest.raises(ValueError):
            validate_dimensions(16.0, 16)  # type: ignore[arg-type]


class TestValidateProjectPath:
    def test_valid_directory(self, tmp_dir):
        validate_project_path(tmp_dir)

    def test_empty_string(self):
        with pytest.raises(ValueError):
            validate_project_path("")

    def test_nonexistent(self, tmp_dir):
        with pytest.raises(ValueError):
            validate_project_path(os.path.join(tmp_dir, "nope"))

    def test_file_not_directory(self, tmp_dir):
        path = os.path.join(tmp_dir, "file.txt")
        open(path, "w").close()
        with pytest.raises(ValueError):
            validate_project_path(path)

    def test_not_writable_directory(self, tmp_dir, monkeypatch):
        monkeypatch.setattr(os, "access", lambda path, mode: False)
        with pytest.raises(ValueError, match="not writable"):
            validate_project_path(tmp_dir)


class TestValidatePngPath:
    def test_valid_png(self, tmp_dir):
        path = os.path.join(tmp_dir, "test.png")
        open(path, "w").close()
        validate_png_path(path)

    def test_empty_string(self):
        with pytest.raises(ValueError):
            validate_png_path("")

    def test_wrong_extension(self, tmp_dir):
        path = os.path.join(tmp_dir, "test.bmp")
        open(path, "w").close()
        with pytest.raises(ValueError, match=".png"):
            validate_png_path(path)

    def test_nonexistent(self, tmp_dir):
        with pytest.raises(ValueError):
            validate_png_path(os.path.join(tmp_dir, "missing.png"))

    def test_path_is_directory(self, tmp_dir, monkeypatch):
        # A path that exists and ends in .png but is not a file
        monkeypatch.setattr(os.path, "isfile", lambda p: False)
        path = os.path.join(tmp_dir, "fake.png")
        open(path, "w").close()
        with pytest.raises(ValueError, match="not a file"):
            validate_png_path(path)

    def test_not_readable(self, tmp_dir, monkeypatch):
        path = os.path.join(tmp_dir, "test.png")
        open(path, "w").close()
        monkeypatch.setattr(os, "access", lambda p, mode: False)
        with pytest.raises(ValueError, match="not readable"):
            validate_png_path(path)


class TestValidateSavePath:
    def test_valid_path(self, tmp_dir):
        validate_save_path(os.path.join(tmp_dir, "out.png"))

    def test_empty_string(self):
        with pytest.raises(ValueError):
            validate_save_path("")

    def test_wrong_extension(self, tmp_dir):
        with pytest.raises(ValueError, match=".png"):
            validate_save_path(os.path.join(tmp_dir, "out.bmp"))

    def test_nonexistent_directory(self):
        with pytest.raises(ValueError):
            validate_save_path("/nonexistent_path_xyz/out.png")

    def test_not_writable_directory(self, tmp_dir, monkeypatch):
        monkeypatch.setattr(os, "access", lambda p, mode: False)
        with pytest.raises(ValueError, match="not writable"):
            validate_save_path(os.path.join(tmp_dir, "out.png"))
