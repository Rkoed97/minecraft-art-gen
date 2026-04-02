"""Load PNG files into PixelImage."""

from PIL import Image, UnidentifiedImageError

from src.models.pixel_image import PixelImage
from src.utils.validators import validate_png_path


def load_png(path: str) -> PixelImage:
    """Load a PNG file and return a PixelImage with RGBA data.

    Raises:
        ValueError: If the path is invalid or the file is not a valid image.
        OSError: If the file cannot be read.
    """
    validate_png_path(path)
    try:
        pil_image = Image.open(path)
        pil_image.load()  # force decode before closing file handle
    except UnidentifiedImageError as exc:
        raise ValueError(f"File is not a valid image: {path!r}") from exc
    return PixelImage.from_pil_image(pil_image)
