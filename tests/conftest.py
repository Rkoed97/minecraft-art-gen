"""Shared test fixtures."""

import os
import tempfile

# Use Qt offscreen platform so tests run without a display
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest

from src.models.pixel_image import PixelImage


@pytest.fixture
def tmp_dir(tmp_path):
    """Provide a temporary directory."""
    return str(tmp_path)


@pytest.fixture
def small_image() -> PixelImage:
    """A 4x4 transparent PixelImage."""
    return PixelImage(4, 4)


@pytest.fixture
def red() -> tuple[int, int, int, int]:
    return (255, 0, 0, 255)


@pytest.fixture
def transparent() -> tuple[int, int, int, int]:
    return (0, 0, 0, 0)
