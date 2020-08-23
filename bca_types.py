"""
Module for types

History:
2020/08/21: v0.0.1
    + add cartography types
"""
from enum import Enum
from typing import List, Optional

from mathutils import Vector


# CLASSES =====================================================================
# Cartography - Commons -------------------------------------------------------
class CartographyCategoryType(Enum):
    """Type of CartographyPointCategory"""
    INTEREST = 1
    STRUCTURAL = 2


class CartographyCategory(bytes, Enum):
    """Category of cartography group or points"""

    def __new__(cls, value: str, cat_type: CartographyCategoryType, outline=False, level=0, face=False):
        obj = bytes.__new__(cls, [value])  # noqa
        obj._value_ = value
        obj.type = cat_type
        obj.outline = outline
        obj.level = level
        obj.face = face
        return obj

    # Structural
    OUTLINE = (1, CartographyCategoryType.STRUCTURAL, True)
    GATE = (2, CartographyCategoryType.STRUCTURAL, True)
    ESCARPMENT = (3, CartographyCategoryType.STRUCTURAL)
    COLUMN = (4, CartographyCategoryType.STRUCTURAL, False, 5, True)
    CHASM = (5, CartographyCategoryType.STRUCTURAL, False, -5, True)

    # Interest
    CLIMBING_POINT = (6, CartographyCategoryType.INTEREST)
    HARVESTABLE = (7, CartographyCategoryType.INTEREST)
    ANTHROPOGENIC_OBJECT = (8, CartographyCategoryType.INTEREST)


class CartographyInterestType(Enum):
    """Type of item (only used by CartographyPoint with category type INTEREST"""
    BOX = 1
    LICHEN = 2
    ORE = 3


# Cartography - Object --------------------------------------------------------
class CartographyObjectType(Enum):
    """Cartography object type"""
    PLANE = 1


# Cartography - Structure -----------------------------------------------------
class CartographyPoint:
    """Point used for cartography"""

    # Constructor -------------------------------------------------------------
    def __init__(
            self,
            name: str,
            category: CartographyCategory,
            location: Vector,
            observations: List[str] = [],  # noqa
            interest_type: CartographyInterestType = None,
    ):
        self.name: str = name
        self.category: CartographyCategory = category
        self.location: Vector = location
        self.observations: List[str] = observations
        self.interest_type: Optional[CartographyInterestType] = interest_type
        self.copy = False

    # Methods -----------------------------------------------------------------
    def __repr__(self):
        return 'CartographyPoint(name={}, category={}, location={}, observations={}, interest_type={})' \
            .format(self.name, self.category, self.location, self.observations, self.interest_type)

    def __str__(self):
        return '{{"name"="{}", "category"={}, "location"={}, "observations"={}, "interest_type"={}}}' \
            .format(self.name, self.category, self.location, self.observations, self.interest_type)


class CartographyGroup:
    """Group of cartography points"""

    # Constructor -------------------------------------------------------------
    def __init__(self, name: str, category: CartographyCategory):
        self.name = name
        self.category = category
        self.points = []

    # Methods -----------------------------------------------------------------
    def __repr__(self):
        return 'CartographyGroup(name={}, category={}, points={})'.format(self.name, self.category, self.points)

    def __str__(self):
        return '{{"name"="{}", "category"={}, "points"={}}}'.format(self.name, self.category, self.points)


class CartographyRoom:
    """Room for cartography"""

    # Constructor -------------------------------------------------------------
    def __init__(self, name: str):
        self.name = name
        self.groups = {}
        self.outline_group: Optional[CartographyGroup] = None

    # Methods -----------------------------------------------------------------
    @property
    def all_points(self) -> List[CartographyPoint]:
        return [p for g in self.groups.values() for p in g.points]


# [UN]REGISTER ================================================================
__classes__ = (
    # CartographyObjectType,
    # CartographyPointCategoryType,
    # CartographyPointCategory,
    # CartographyInterestType,
    # CartographyPoint,
    # CartographyRoom,
)
