"""
Module for common cartography models
"""
from enum import Enum, Flag, auto


# CLASSES =====================================================================
class CartographyCategoryType(Flag):
    """Type of CartographyCategory"""
    INTEREST = auto()
    STRUCTURAL = auto()
    UNKNOWN = auto()


class CartographyCategory(bytes, Enum):
    """Category of cartography group or points"""

    # TODO outline/level/top_face only used for structural
    def __new__(
            cls, value: str, cat_type: CartographyCategoryType,  # required
            outline=False, level=0, ground=False  # options
    ):
        obj = bytes.__new__(cls, [value])  # noqa
        obj._value_ = value
        obj.type = cat_type
        obj.outline = outline
        obj.level = level
        obj.ground = ground
        return obj

    # Structural
    OUTLINE = (1, CartographyCategoryType.STRUCTURAL, True, 2, True)  # outline
    GATE = (2, CartographyCategoryType.STRUCTURAL, True)  # outline
    ESCARPMENT = (3, CartographyCategoryType.STRUCTURAL, False, 0, True)  # leveled
    BASEMENT = (4, CartographyCategoryType.STRUCTURAL, False, 0, True)  # leveled
    LANDING = (5, CartographyCategoryType.STRUCTURAL, False, 0, True)  # leveled
    COLUMN = (6, CartographyCategoryType.STRUCTURAL, False, 5)  # extruded
    COLUMN_BASE = (7, CartographyCategoryType.STRUCTURAL, False, 0, True)  # leveled
    CHASM = (8, CartographyCategoryType.STRUCTURAL, False, -5, True)  # extruded

    RECESS = (9, CartographyCategoryType.STRUCTURAL & CartographyCategoryType.INTEREST)

    # Interest
    CLIMBING_POINT = (10, CartographyCategoryType.INTEREST)
    HARVESTABLE = (11, CartographyCategoryType.INTEREST)
    ANTHROPOGENIC_OBJECT = (12, CartographyCategoryType.INTEREST)
    BANK = (13, CartographyCategoryType.INTEREST)
    STRUCTURE = (14, CartographyCategoryType.INTEREST)

    # Others
    UNKNOWN = (99, CartographyCategoryType.UNKNOWN)


class CartographyInterestType(Enum):
    """Type of item (only used by CartographyPoint with category type INTEREST)"""
    BOX = 1
    LITTLE_BOX = 2
    LICHEN = 3
    ORE = 4
