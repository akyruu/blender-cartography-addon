"""
Module for common cartography models
"""
from enum import Enum, Flag, auto


# CLASSES =====================================================================
class CartographyCategoryType(Flag):
    """Type of CartographyCategory"""
    INTEREST = auto()
    STRUCTURAL = auto()
    STRUCTURAL_INTEREST = STRUCTURAL & INTEREST

    UNKNOWN = auto()


class CartographyCategoryOptions:
    def __init__(self, outline=False, level=0, ground=False, separated=False):
        self.outline = outline
        self.level = level
        self.ground = ground
        self.separated = separated


class CartographyCategoryOptionsFactory:
    @staticmethod
    def leveled() -> CartographyCategoryOptions:
        return CartographyCategoryOptions(ground=True)

    @staticmethod
    def extruded(level: int, ground: bool) -> CartographyCategoryOptions:
        return CartographyCategoryOptions(level=level, ground=ground)

    @staticmethod
    def outline(level: int, ground: bool) -> CartographyCategoryOptions:
        return CartographyCategoryOptions(outline=True, level=level, ground=ground)

    @staticmethod
    def separated() -> CartographyCategoryOptions:
        return CartographyCategoryOptions(separated=True)


class CartographyCategory(bytes, Enum):
    """Category of cartography group or points"""

    # TODO outline/level/top_face only used for structural
    def __new__(cls, value: str, cat_type: CartographyCategoryType, options=None):
        obj = bytes.__new__(cls, [value])  # noqa
        obj._value_ = value
        obj.type = cat_type
        obj.options = options or CartographyCategoryOptions()
        return obj

    # Structural
    OUTLINE = 1, CartographyCategoryType.STRUCTURAL, CartographyCategoryOptionsFactory.outline(2, True)
    GATE = 2, CartographyCategoryType.STRUCTURAL, CartographyCategoryOptionsFactory.outline(0, False)
    ESCARPMENT = 3, CartographyCategoryType.STRUCTURAL, CartographyCategoryOptionsFactory.leveled()
    BASEMENT = 4, CartographyCategoryType.STRUCTURAL, CartographyCategoryOptionsFactory.leveled()
    LANDING = 5, CartographyCategoryType.STRUCTURAL, CartographyCategoryOptionsFactory.leveled()
    COLUMN = 6, CartographyCategoryType.STRUCTURAL, CartographyCategoryOptionsFactory.extruded(5, False)
    COLUMN_BASE = 7, CartographyCategoryType.STRUCTURAL, CartographyCategoryOptionsFactory.leveled()
    CHASM = 8, CartographyCategoryType.STRUCTURAL, CartographyCategoryOptionsFactory.extruded(-5, True)

    # Structural/Interest
    RECESS = 20, CartographyCategoryType.STRUCTURAL_INTEREST
    BANK = 21, CartographyCategoryType.STRUCTURAL_INTEREST, CartographyCategoryOptionsFactory.separated()

    # Interest
    CLIMBING_POINT = 40, CartographyCategoryType.INTEREST
    HARVESTABLE = 41, CartographyCategoryType.INTEREST
    ANTHROPOGENIC_OBJECT = 42, CartographyCategoryType.INTEREST
    STRUCTURE = 43, CartographyCategoryType.INTEREST

    # Others
    UNKNOWN = 99, CartographyCategoryType.UNKNOWN


class CartographyInterestType(Enum):
    """Type of item (only used by CartographyPoint with category type INTEREST)"""
    # Structure
    BOX = auto()
    LITTLE_BOX = auto()

    # Harvestable
    LICHEN = auto()
    ORE = auto()

    # Others
    UNKNOWN = auto()
