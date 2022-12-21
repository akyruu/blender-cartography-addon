"""
Module for structure cartography models
"""
from typing import Dict, List, Optional, Tuple

import utils
from mathutils import Vector
from .common import CartographyInterestType, CartographyCategory


# CLASSES =====================================================================
class CartographyPoint:
    """Point used for cartography"""

    # Constructor -------------------------------------------------------------
    def __init__(
            self,
            name: str = None,
            comments: str = None,
            category: CartographyCategory = None,
            location: Vector = Vector((0, 0, 0)),
            observations: List[str] = None,
            interest: Optional[Tuple[CartographyInterestType, int]] = None,
            additional_categories: List[CartographyCategory] = []  # noqa
    ):
        self.name: str = name
        self.comments: List[str] = comments or []
        self.category = category
        self.location = location
        self.observations = observations or []
        self.interest = interest
        self.extra_categories = additional_categories
        self.copy = False

    # Methods -----------------------------------------------------------------
    def get_label(self):
        return self.name + (' (' + ', '.join(self.comments) + ')' if self.comments else '')

    def has_category(self, category: CartographyCategory):
        return category == self.category or category in self.extra_categories

    def __repr__(self):
        return utils.object.to_repr(self)

    def __str__(self):
        return utils.object.to_str(self)


class CartographyGroup:
    """Group of cartography points"""

    # Constructor -------------------------------------------------------------
    def __init__(self, name: str, category: CartographyCategory, category_number: int, linked: List[any] = None):
        self.name = name
        self.category = category
        self.category_number = category_number
        self.points = []
        self.linked: List[CartographyGroup] = linked or []

    # Methods -----------------------------------------------------------------
    def __repr__(self):
        return utils.object.to_repr(self)

    def __str__(self):
        return utils.object.to_str(self)


class CartographyJunction:
    """Junction points between two groups"""

    # Constructor -------------------------------------------------------------
    def __init__(self, group1: CartographyGroup, group2: CartographyGroup):
        self.group1 = group1
        self.group2 = group2
        self.groups = (group1, group2)

        self.points1: List[CartographyPoint] = []
        self.points2: List[CartographyPoint] = []
        self.points: List[Tuple[CartographyPoint, CartographyPoint]] = []

    # Methods -----------------------------------------------------------------
    def add_points(self, point1: CartographyPoint, point2: CartographyPoint):
        self.points1.append(point1)
        self.points2.append(point2)
        self.points.append((point1, point2))

    def has_point(self, point: CartographyPoint):
        loc = point.location
        return utils.collection.list.pnext(self.points, lambda p: loc in [p.location for p in p]) is not None

    def __repr__(self):
        return utils.object.to_repr(self)

    def __str__(self):
        return utils.object.to_str(self)


class CartographyRoom:
    """Room for cartography"""

    # Constructor -------------------------------------------------------------
    def __init__(self, name: str):
        self.name = name
        self.groups: Dict[str, CartographyGroup] = {}
        self.outline_group: Optional[CartographyGroup] = None
        self.junctions: List[CartographyJunction] = []

    # Methods -----------------------------------------------------------------
    @property
    def all_points(self) -> List[CartographyPoint]:
        return [p for g in self.groups.values() for p in g.points]

    def add_junction(self, group1: CartographyGroup, group2: CartographyGroup) -> CartographyJunction:
        junction = CartographyJunction(group1, group2)
        self.junctions.append(junction)
        return junction

    def get_junction(self, group1: CartographyGroup, group2: CartographyGroup) -> CartographyJunction:
        return utils.collection.list.pnext(self.junctions, lambda j: group1 in j.groups and group2 in j.groups)

    def has_junction(self, group1: CartographyGroup, group2: Optional[CartographyGroup] = None) -> bool:
        predicate = (lambda j: group1 in j.groups) \
            if not group2 \
            else (lambda j: group1 in j.groups and group2 in j.groups)
        return utils.collection.list.pnext(self.junctions, predicate) is not None

    def __repr__(self):
        return utils.object.to_repr(self)

    def __str__(self):
        return utils.object.to_str(self)
