"""
Module for structure cartography models
"""
from typing import List, Optional, Tuple

from mathutils import Vector

import utils
from .common import CartographyInterestType, CartographyCategory


# CLASSES =====================================================================
class CartographyPoint:
    """Point used for cartography"""

    # Constructor -------------------------------------------------------------
    def __init__(
            self,
            name: str = None,
            category: CartographyCategory = None,
            location: Vector = Vector((0, 0, 0)),
            observations: List[str] = (),
            interest: Optional[Tuple[CartographyInterestType, int]] = None,
    ):
        self.name: str = name
        self.category = category
        self.location = location
        self.observations = observations
        self.interest = interest
        self.copy = False

    # Methods -----------------------------------------------------------------
    def __repr__(self):
        return utils.object.to_repr(self)

    def __str__(self):
        return utils.object.to_str(self)


class CartographyGroup:
    """Group of cartography points"""

    # Constructor -------------------------------------------------------------
    def __init__(self, name: str, category: CartographyCategory):
        self.name = name
        self.category = category
        self.points = []

    # Methods -----------------------------------------------------------------
    def __repr__(self):
        return utils.object.to_repr(self)

    def __str__(self):
        return utils.object.to_str(self)


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

    def __repr__(self):
        return utils.object.to_repr(self)

    def __str__(self):
        return utils.object.to_str(self)
