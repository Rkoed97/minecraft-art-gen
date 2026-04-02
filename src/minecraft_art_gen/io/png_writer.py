"""Save PixelImage to PNG files."""

from minecraft_art_gen.models.pixel_image import PixelImage
from minecraft_art_gen.utils.validators import validate_save_path


def save_png(image: PixelImage, path: str) -> None:
    """Save a PixelImage as a PNG file with full RGBA data.

    The file is written atomically: first to a temporary file, then renamed,
    so a failed save does not corrupt an existing file.

    Raises:
        ValueError: If the path is invalid.
        OSError: If the file cannot be written.
    """
    validate_save_path(path)
    import os
    import tempfile

    pil_image = image.to_pil_image()

    dir_name = os.path.dirname(os.path.abspath(path))
    fd, tmp_path = tempfile.mkstemp(dir=dir_name, suffix=".png.tmp")
    try:
        os.close(fd)
        pil_image.save(tmp_path, format="PNG", optimize=False)
        os.replace(tmp_path, path)
    except Exception:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise
