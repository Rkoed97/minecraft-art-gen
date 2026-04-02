"""Input validation utilities for paths and canvas dimensions."""

import os

MAX_DIMENSION = 512


def validate_dimensions(width: int, height: int) -> None:
    """Raise ValueError if dimensions are invalid."""
    if not isinstance(width, int) or not isinstance(height, int):
        raise ValueError("Dimensions must be integers")
    if width <= 0 or height <= 0:
        raise ValueError(f"Dimensions must be positive, got {width}x{height}")
    if width > MAX_DIMENSION or height > MAX_DIMENSION:
        raise ValueError(
            f"Dimensions exceed maximum of {MAX_DIMENSION}x{MAX_DIMENSION}, got {width}x{height}"
        )


def validate_project_path(path: str) -> None:
    """Raise ValueError if path is not a writable directory."""
    if not path:
        raise ValueError("Project path must not be empty")
    if not os.path.exists(path):
        raise ValueError(f"Path does not exist: {path!r}")
    if not os.path.isdir(path):
        raise ValueError(f"Path is not a directory: {path!r}")
    if not os.access(path, os.W_OK):
        raise ValueError(f"Path is not writable: {path!r}")


def validate_png_path(path: str) -> None:
    """Raise ValueError if path does not point to a readable .png file."""
    if not path:
        raise ValueError("PNG path must not be empty")
    if not path.lower().endswith(".png"):
        raise ValueError(f"File does not have a .png extension: {path!r}")
    if not os.path.exists(path):
        raise ValueError(f"File does not exist: {path!r}")
    if not os.path.isfile(path):
        raise ValueError(f"Path is not a file: {path!r}")
    if not os.access(path, os.R_OK):
        raise ValueError(f"File is not readable: {path!r}")


def validate_save_path(path: str) -> None:
    """Raise ValueError if path cannot be used as a PNG save destination."""
    if not path:
        raise ValueError("Save path must not be empty")
    if not path.lower().endswith(".png"):
        raise ValueError(f"Save path must end with .png: {path!r}")
    directory = os.path.dirname(os.path.abspath(path))
    if not os.path.exists(directory):
        raise ValueError(f"Parent directory does not exist: {directory!r}")
    if not os.access(directory, os.W_OK):
        raise ValueError(f"Parent directory is not writable: {directory!r}")
