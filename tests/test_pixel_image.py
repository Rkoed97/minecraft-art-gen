"""Tests for PixelImage model."""

import pytest

from src.models.pixel_image import PixelImage, TRANSPARENT


RED = (255, 0, 0, 255)
GREEN = (0, 255, 0, 255)
SEMI_TRANSPARENT = (100, 150, 200, 128)


class TestConstruction:
    def test_default_fill_is_transparent(self):
        img = PixelImage(2, 3)
        for y in range(3):
            for x in range(2):
                assert img.get_pixel(x, y) == TRANSPARENT

    def test_custom_fill(self):
        img = PixelImage(2, 2, fill=RED)
        assert img.get_pixel(0, 0) == RED
        assert img.get_pixel(1, 1) == RED

    def test_zero_width_raises(self):
        with pytest.raises(ValueError):
            PixelImage(0, 4)

    def test_zero_height_raises(self):
        with pytest.raises(ValueError):
            PixelImage(4, 0)

    def test_negative_raises(self):
        with pytest.raises(ValueError):
            PixelImage(-1, 4)

    def test_size_property(self):
        img = PixelImage(3, 7)
        assert img.size == (3, 7)
        assert img.width == 3
        assert img.height == 7


class TestFromData:
    def test_round_trip(self):
        pixels = [RED, GREEN, TRANSPARENT, SEMI_TRANSPARENT]
        img = PixelImage.from_data(2, 2, pixels)
        assert img.get_pixel(0, 0) == RED
        assert img.get_pixel(1, 0) == GREEN
        assert img.get_pixel(0, 1) == TRANSPARENT
        assert img.get_pixel(1, 1) == SEMI_TRANSPARENT

    def test_wrong_pixel_count_raises(self):
        with pytest.raises(ValueError):
            PixelImage.from_data(2, 2, [RED, GREEN])  # only 2, needs 4


class TestSetPixel:
    def test_returns_new_instance(self, small_image):
        new_img = small_image.set_pixel(0, 0, RED)
        assert new_img is not small_image

    def test_original_unchanged(self, small_image):
        small_image.set_pixel(0, 0, RED)
        assert small_image.get_pixel(0, 0) == TRANSPARENT

    def test_new_has_correct_pixel(self, small_image):
        new_img = small_image.set_pixel(1, 2, RED)
        assert new_img.get_pixel(1, 2) == RED

    def test_other_pixels_unchanged(self, small_image):
        new_img = small_image.set_pixel(1, 2, RED)
        assert new_img.get_pixel(0, 0) == TRANSPARENT
        assert new_img.get_pixel(3, 3) == TRANSPARENT

    def test_out_of_bounds_raises(self, small_image):
        with pytest.raises(IndexError):
            small_image.set_pixel(4, 0, RED)

    def test_invalid_color_raises(self, small_image):
        with pytest.raises(ValueError):
            small_image.set_pixel(0, 0, (256, 0, 0, 255))

    def test_alpha_preserved(self, small_image):
        new_img = small_image.set_pixel(0, 0, SEMI_TRANSPARENT)
        assert new_img.get_pixel(0, 0) == SEMI_TRANSPARENT


class TestSetPixels:
    def test_bulk_paint(self, small_image):
        coords = [(0, 0), (1, 1), (2, 2)]
        new_img = small_image.set_pixels(coords, RED)
        for x, y in coords:
            assert new_img.get_pixel(x, y) == RED
        assert new_img.get_pixel(3, 3) == TRANSPARENT

    def test_empty_coords(self, small_image):
        new_img = small_image.set_pixels([], RED)
        assert new_img == small_image


class TestClearPixel:
    def test_clears_to_transparent(self):
        img = PixelImage(2, 2, fill=RED)
        new_img = img.clear_pixel(0, 0)
        assert new_img.get_pixel(0, 0) == TRANSPARENT
        assert new_img.get_pixel(1, 1) == RED

    def test_returns_new_instance(self):
        img = PixelImage(2, 2, fill=RED)
        new_img = img.clear_pixel(0, 0)
        assert new_img is not img


class TestClearPixels:
    def test_bulk_clear(self):
        img = PixelImage(3, 3, fill=RED)
        coords = [(0, 0), (1, 1)]
        new_img = img.clear_pixels(coords)
        assert new_img.get_pixel(0, 0) == TRANSPARENT
        assert new_img.get_pixel(1, 1) == TRANSPARENT
        assert new_img.get_pixel(2, 2) == RED


class TestResize:
    def test_grow_pads_with_transparent(self):
        img = PixelImage(2, 2, fill=RED)
        bigger = img.resize(4, 4)
        assert bigger.size == (4, 4)
        assert bigger.get_pixel(0, 0) == RED
        assert bigger.get_pixel(1, 1) == RED
        assert bigger.get_pixel(2, 2) == TRANSPARENT

    def test_shrink_clips_content(self):
        img = PixelImage(4, 4, fill=RED)
        smaller = img.resize(2, 2)
        assert smaller.size == (2, 2)
        assert smaller.get_pixel(0, 0) == RED
        assert smaller.get_pixel(1, 1) == RED

    def test_same_size_identical(self):
        img = PixelImage(3, 3, fill=RED)
        same = img.resize(3, 3)
        assert same == img

    def test_original_unchanged(self):
        img = PixelImage(2, 2, fill=RED)
        img.resize(4, 4)
        assert img.size == (2, 2)

    def test_invalid_raises(self):
        img = PixelImage(2, 2)
        with pytest.raises(ValueError):
            img.resize(0, 2)


class TestEquality:
    def test_equal_images(self):
        a = PixelImage(2, 2, fill=RED)
        b = PixelImage(2, 2, fill=RED)
        assert a == b

    def test_different_pixels_not_equal(self):
        a = PixelImage(2, 2, fill=RED)
        b = a.set_pixel(0, 0, GREEN)
        assert a != b

    def test_different_size_not_equal(self):
        a = PixelImage(2, 2)
        b = PixelImage(3, 2)
        assert a != b
