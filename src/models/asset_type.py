from dataclasses import dataclass, field


@dataclass(frozen=True)
class AssetType:
    name: str
    description: str
    default_width: int
    default_height: int
    # All supported (width, height) variants. First entry is the default.
    variants: tuple[tuple[int, int], ...]

    @property
    def default_size(self) -> tuple[int, int]:
        return (self.default_width, self.default_height)


ASSET_TYPES: dict[str, AssetType] = {
    "block": AssetType(
        name="Block",
        description="Block texture (16x16 standard, higher-res for resource packs)",
        default_width=16,
        default_height=16,
        variants=(
            (16, 16),
            (32, 32),
            (64, 64),
            (128, 128),
            (256, 256),
        ),
    ),
    "item": AssetType(
        name="Item",
        description="Item texture (16x16 standard, higher-res for resource packs)",
        default_width=16,
        default_height=16,
        variants=(
            (16, 16),
            (32, 32),
            (64, 64),
            (128, 128),
        ),
    ),
    "entity_classic": AssetType(
        name="Entity (Classic Mob)",
        description="Classic mob skin sheet (e.g. creeper, skeleton)",
        default_width=64,
        default_height=32,
        variants=((64, 32),),
    ),
    "entity_humanoid": AssetType(
        name="Entity (Humanoid)",
        description="Humanoid mob skin sheet (e.g. villager, zombie)",
        default_width=64,
        default_height=64,
        variants=((64, 64),),
    ),
    "gui": AssetType(
        name="GUI Element",
        description="GUI screen texture (e.g. inventory, container backgrounds)",
        default_width=256,
        default_height=256,
        variants=((256, 256),),
    ),
    "effect_icon": AssetType(
        name="Effect Icon",
        description="Status effect icon",
        default_width=18,
        default_height=18,
        variants=((18, 18),),
    ),
    "painting_small": AssetType(
        name="Painting (1x1 — Small)",
        description="1x1 block painting (Kebab, Aztec, etc.)",
        default_width=16,
        default_height=16,
        variants=((16, 16),),
    ),
    "painting_medium": AssetType(
        name="Painting (2x1 — Medium)",
        description="2x1 block painting (Aztec2, Alban, etc.)",
        default_width=32,
        default_height=16,
        variants=((32, 16),),
    ),
    "painting_wide": AssetType(
        name="Painting (3x1 — Wide)",
        description="3x1 block painting (Bomb, Plant, etc.)",
        default_width=48,
        default_height=16,
        variants=((48, 16),),
    ),
    "painting_large": AssetType(
        name="Painting (4x2 — Large)",
        description="4x2 block painting (Wasteland, Pool, etc.)",
        default_width=64,
        default_height=32,
        variants=((64, 32),),
    ),
    "painting_grand": AssetType(
        name="Painting (4x4 — Grand)",
        description="4x4 block painting (Skeleton, Donkey Kong, etc.)",
        default_width=64,
        default_height=64,
        variants=((64, 64),),
    ),
    "particle": AssetType(
        name="Particle",
        description="Particle texture sprite",
        default_width=8,
        default_height=8,
        variants=((8, 8),),
    ),
    "trim": AssetType(
        name="Armor Trim",
        description="Armor trim pattern texture",
        default_width=16,
        default_height=32,
        variants=(
            (16, 32),
            (32, 64),
            (64, 128),
        ),
    ),
}

# Ordered list for display in UI
ASSET_TYPE_ORDER: list[str] = [
    "block",
    "item",
    "entity_classic",
    "entity_humanoid",
    "gui",
    "effect_icon",
    "painting_small",
    "painting_medium",
    "painting_wide",
    "painting_large",
    "painting_grand",
    "particle",
    "trim",
]
