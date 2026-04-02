"""Tests for asset type registry."""

import pytest

from src.models.asset_type import ASSET_TYPES, ASSET_TYPE_ORDER, AssetType


class TestAssetTypeDataclass:
    def test_is_frozen(self):
        at = ASSET_TYPES["block"]
        with pytest.raises((AttributeError, TypeError)):
            at.name = "changed"  # type: ignore[misc]

    def test_default_size_matches_first_variant(self):
        for key, at in ASSET_TYPES.items():
            assert at.default_size == at.variants[0], f"{key}: default_size != variants[0]"

    def test_all_variants_positive(self):
        for key, at in ASSET_TYPES.items():
            for w, h in at.variants:
                assert w > 0 and h > 0, f"{key} has non-positive variant ({w}, {h})"


class TestAssetTypeRegistry:
    def test_all_order_keys_in_registry(self):
        for key in ASSET_TYPE_ORDER:
            assert key in ASSET_TYPES, f"{key!r} missing from ASSET_TYPES"

    def test_registry_keys_match_order(self):
        assert set(ASSET_TYPE_ORDER) == set(ASSET_TYPES.keys())

    def test_block_has_higher_res_variants(self):
        block = ASSET_TYPES["block"]
        assert (16, 16) in block.variants
        assert (32, 32) in block.variants
        assert (64, 64) in block.variants
        assert (128, 128) in block.variants
        assert (256, 256) in block.variants

    def test_item_has_higher_res_variants(self):
        item = ASSET_TYPES["item"]
        assert (16, 16) in item.variants
        assert (32, 32) in item.variants
        assert (64, 64) in item.variants
        assert (128, 128) in item.variants

    def test_trim_has_higher_res_variants(self):
        trim = ASSET_TYPES["trim"]
        assert (16, 32) in trim.variants
        assert (32, 64) in trim.variants
        assert (64, 128) in trim.variants

    def test_default_sizes(self):
        expected = {
            "block": (16, 16),
            "item": (16, 16),
            "entity_classic": (64, 32),
            "entity_humanoid": (64, 64),
            "gui": (256, 256),
            "effect_icon": (18, 18),
            "painting_small": (16, 16),
            "painting_medium": (32, 16),
            "painting_wide": (48, 16),
            "painting_large": (64, 32),
            "painting_grand": (64, 64),
            "particle": (8, 8),
            "trim": (16, 32),
        }
        for key, size in expected.items():
            assert ASSET_TYPES[key].default_size == size, f"{key} default size mismatch"

    def test_count(self):
        assert len(ASSET_TYPES) == 13
