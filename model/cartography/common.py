"""
Module for common cartography models
"""
from enum import Enum


# CLASSES =====================================================================
class CartographyCategoryType(Enum):
    """Type of CartographyPointCategory"""
    INTEREST = 1
    STRUCTURAL = 2


class CartographyCategory(bytes, Enum):
    """Category of cartography group or points"""

    def __new__(cls, value: str, cat_type: CartographyCategoryType, outline=False, level=0, top_face=False):
        obj = bytes.__new__(cls, [value])  # noqa
        obj._value_ = value
        obj.type = cat_type
        obj.outline = outline
        obj.level = level
        obj.top_face = top_face
        return obj

    # Structural
    OUTLINE = (1, CartographyCategoryType.STRUCTURAL, True)
    GATE = (2, CartographyCategoryType.STRUCTURAL, True)
    ESCARPMENT = (3, CartographyCategoryType.STRUCTURAL)
    BASEMENT = (4, CartographyCategoryType.STRUCTURAL)
    COLUMN = (5, CartographyCategoryType.STRUCTURAL, False, 5, False)
    CHASM = (6, CartographyCategoryType.STRUCTURAL, False, -5, True)

    # Interest
    CLIMBING_POINT = (10, CartographyCategoryType.INTEREST)
    HARVESTABLE = (11, CartographyCategoryType.INTEREST)
    ANTHROPOGENIC_OBJECT = (12, CartographyCategoryType.INTEREST)
    BANK = (13, CartographyCategoryType.INTEREST)
    STRUCTURE = (14, CartographyCategoryType.INTEREST)


class CartographyInterestType(Enum):
    """Type of item (only used by CartographyPoint with category type INTEREST)"""
    BOX = 1
    LITTLE_BOX = 2
    LICHEN = 3
    ORE = 4