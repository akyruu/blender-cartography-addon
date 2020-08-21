"""
Module for types

History:
2020/08/21: v0.0.1
    + add cartography types
"""

from enum import Enum


# CLASSES =====================================================================
# Cartography - Object --------------------------------------------------------
class CartographyObjectType(Enum):
    """Cartography object type"""
    PLANE = 1


# Cartography - Point ---------------------------------------------------------
class CartographyPointCategoryType(Enum):
    """Type of CartographyPointCategory"""
    INTEREST = 1
    STRUCTURAL = 2


class CartographyPointCategory(bytes, Enum):
    """Category of CartographyPoint"""

    def __new__(cls, value: str, cat_type: CartographyPointCategoryType, outline=False, level=0, face=False):
        obj = bytes.__new__(cls, [value])
        obj._value_ = value
        obj.type = cat_type
        obj.outline = outline
        obj.level = level
        obj.face = face
        return obj

    # Structural
    OUTLINE = (1, CartographyPointCategoryType.STRUCTURAL, True)
    GATE = (2, CartographyPointCategoryType.STRUCTURAL, True)
    ESCARPMENT = (3, CartographyPointCategoryType.STRUCTURAL)
    COLUMN = (4, CartographyPointCategoryType.STRUCTURAL, False, 5, True)
    CHASM = (5, CartographyPointCategoryType.STRUCTURAL, False, -5, True)

    # Interest
    CLIMBING_POINT = (6, CartographyPointCategoryType.INTEREST)
    HARVESTABLE = (7, CartographyPointCategoryType.INTEREST)
    ANTHROPOGENIC_OBJECT = (8, CartographyPointCategoryType.INTEREST)


class CartographyInterestType(Enum):
    """Type of item (only used by CartographyPoint with category type INTEREST"""
    BOX = 1
    LICHEN = 2
    ORE = 3


class CartographyPoint:
    """Point used for cartography"""

    # Constructor -------------------------------------------------------------
    def __init__(self,
                 name: str,
                 category: CartographyPointCategory,
                 x: int,
                 y: int,
                 z: int,
                 interest_type: CartographyInterestType = None
                 ):
        self.name = name
        self.category = category
        self.x = x
        self.y = y
        self.z = z
        self.interest_type = interest_type

    # Methods -----------------------------------------------------------------
    def __str__(self):
        return '<carto-point' \
               + ' name="' + self.name + '"' \
               + ' category="' + self.category.name + '"' \
               + ' x=' + str(self.x) + ' y=' + str(self.y) + ' z=' + str(self.z) \
               + (' item-type="' + self.itemType.name + '"' if self.itemType else '') \
               + ' />'


class CartographyRoom:
    # Constructor -------------------------------------------------------------
    def __init__(self, name: str):
        self.name = name
        self.points = []


# [UN]REGISTER ================================================================
__classes__ = (
    # CartographyObjectType,
    # CartographyPointCategoryType,
    # CartographyPointCategory,
    # CartographyInterestType,
    # CartographyPoint,
    # CartographyRoom,
)
