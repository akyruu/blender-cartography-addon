"""
Module for common cartography models
"""
from enum import Enum, Flag, auto
from typing import Optional


# Type ------------------------------------------------------------------------
class CartographyCategoryType(Flag):
    """Types of CartographyCategory"""
    INTEREST = auto()
    STRUCTURAL = auto()
    UNKNOWN = auto()


# Options ---------------------------------------------------------------------
class CartographyCategoryOptions:
    """Options of CartographyCategory"""


class CartographyInterestCategoryOptions(CartographyCategoryOptions):
    """Options of CartographyCategory with type CartographyCategoryType#INTEREST"""

    def __init__(self, detailed_required=False, structured=False):
        self.detailed_required = detailed_required
        self.structured = structured

    @staticmethod
    def structured():
        return CartographyInterestCategoryOptions(structured=True)

    @staticmethod
    def detailed(required: bool):
        return CartographyInterestCategoryOptions(detailed_required=required)


class CartographyStructuralCategoryOptions(CartographyCategoryOptions):
    """Options of CartographyCategory with type CartographyCategoryType#STRUCTURAL"""

    def __init__(self, outline=False, level=0, ground=False):
        self.outline = outline
        self.level = level
        self.ground = ground

    @staticmethod
    def outlined(level=0, ground=False):
        return CartographyStructuralCategoryOptions(outline=True, level=level, ground=ground)

    @staticmethod
    def leveled():
        return CartographyStructuralCategoryOptions(ground=True)

    @staticmethod
    def extruded(level: int, ground):
        return CartographyStructuralCategoryOptions(level=level, ground=ground)


# Category --------------------------------------------------------------------

class CartographyCategory(bytes, Enum):
    """Category of cartography group or points"""

    def __new__(cls, value: int, cat_type: CartographyCategoryType, options=CartographyCategoryOptions()):
        obj = bytes.__new__(cls, [value])  # noqa
        obj._value_ = value
        obj.type = cat_type
        obj.options = options
        return obj

    # Structural
    OUTLINE = (1, CartographyCategoryType.STRUCTURAL, CartographyStructuralCategoryOptions.outlined(2, True))
    GATE = (2, CartographyCategoryType.STRUCTURAL, CartographyStructuralCategoryOptions.outlined())
    ESCARPMENT = (3, CartographyCategoryType.STRUCTURAL, CartographyStructuralCategoryOptions.leveled())
    BASEMENT = (4, CartographyCategoryType.STRUCTURAL, CartographyStructuralCategoryOptions.leveled())
    LANDING = (5, CartographyCategoryType.STRUCTURAL, CartographyStructuralCategoryOptions.leveled())
    COLUMN = (6, CartographyCategoryType.STRUCTURAL, CartographyStructuralCategoryOptions.extruded(5, False))
    COLUMN_BASE = (7, CartographyCategoryType.STRUCTURAL, CartographyStructuralCategoryOptions.leveled())
    CHASM = (8, CartographyCategoryType.STRUCTURAL, CartographyStructuralCategoryOptions.extruded(-5, True))

    # Structural/Interest
    BANK = (9, CartographyCategoryType.INTEREST, CartographyInterestCategoryOptions.structured())
    RECESS = (10, CartographyCategoryType.INTEREST, CartographyInterestCategoryOptions.structured())

    # Interest
    CLIMBING_POINT = (11, CartographyCategoryType.INTEREST, CartographyInterestCategoryOptions())
    HARVESTABLE = (12, CartographyCategoryType.INTEREST, CartographyInterestCategoryOptions.detailed(True))
    ANTHROPOGENIC_OBJECT = (13, CartographyCategoryType.INTEREST, CartographyInterestCategoryOptions.detailed(True))
    STRUCTURE = (14, CartographyCategoryType.INTEREST, CartographyInterestCategoryOptions.detailed(True))

    # Others
    UNKNOWN = (99, CartographyCategoryType.UNKNOWN, CartographyCategoryOptions())


# Interest --------------------------------------------------------------------
class CartographyInterestType(bytes, Enum):
    """Type of item (only used by CartographyPoint with category type INTEREST)"""

    def __new__(cls, value: int, category: Optional[CartographyCategory]):
        obj = bytes.__new__(cls, [value])  # noqa
        obj._value_ = value
        obj.category = category
        return obj

    # Anthropogenic object
    BOX = (1, CartographyCategory.ANTHROPOGENIC_OBJECT)
    LITTLE_BOX = (2, CartographyCategory.ANTHROPOGENIC_OBJECT)
    # Harvestable
    LICHEN = (3, CartographyCategory.HARVESTABLE)
    ORE = (4, CartographyCategory.HARVESTABLE)
    # Others
    UNKNOWN = (99, None)
