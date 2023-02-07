"""
Module for structure cartography models
"""
from typing import Dict, List, Optional, Set, Tuple

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
            group_identifier: int = 0,
            comments: str = None,
            category: CartographyCategory = None,
            location: Vector = Vector((0, 0, 0)),
            observations: List[str] = None,
            interest: Optional[CartographyInterestType] = None,
            additional_categories: Optional[Set[CartographyCategory]] = None,
    ):
        self.name: str = name
        self.group_identifier = group_identifier
        self.comments: List[str] = comments or []
        self.category = category
        self.location = location
        self.observations = observations or []
        self.interest = interest
        self.additional_categories = additional_categories or set([])
        self.copy = False

    # Methods -----------------------------------------------------------------
    def get_label(self):
        return self.name + (' (' + ', '.join(self.comments) + ')' if self.comments else '')

    def has_category(self, category: CartographyCategory):
        return category == self.category or category in self.additional_categories

    def get_all_categories(self):
        return set([self.category] + list(self.additional_categories))

    def is_same(self, other) -> bool:
        return other and isinstance(other, CartographyPoint) \
            and self.category == other.category \
            and self.interest == other.interest \
            and self.group_identifier == other.group_identifier \
            and utils.math.same_3d_position(self.location, other.location)

    def __repr__(self):
        return utils.object.to_repr(self)

    def __str__(self):
        return utils.object.to_str(self)


class CartographyGroup:
    """Group of cartography points"""

    # Constructor -------------------------------------------------------------
    def __init__(self, name: str, category: CartographyCategory, linked: List[any] = None):
        self.name = name
        self.category = category
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

    def has_same_point(self, point: CartographyPoint) -> bool:
        return next((1 for (p1, p2) in self.points if p1.is_same(point) or p2.is_same(point)), None) is not None

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

    def remove_point(self, point: CartographyPoint) -> bool:
        removed = False
        for group in self.groups.values():
            if point in group.points:
                group.points.remove(point)
                removed = True
                break
        if removed:
            junctions_to_remove = [j for j in self.junctions if j.has_same_point(point)]
            for junction in junctions_to_remove:
                self.junctions.remove(junction)

        return removed

    def add_junction(self, group1: CartographyGroup, group2: CartographyGroup) -> CartographyJunction:
        junction = CartographyJunction(group1, group2)
        self.junctions.append(junction)
        return junction

    def get_junction(self, group1: CartographyGroup, group2: CartographyGroup) -> CartographyJunction:
        return next((j for j in self.junctions if group1 in j.groups and group2 in j.groups), None)

    def has_junction(self, group1: CartographyGroup, group2: Optional[CartographyGroup] = None) -> bool:
        predicate = (lambda j: group1 in j.groups) \
            if not group2 \
            else (lambda j: group1 in j.groups and group2 in j.groups)
        return next((j for j in self.junctions if predicate(j)), None) is not None

    def __repr__(self):
        return utils.object.to_repr(self)

    def __str__(self):
        return utils.object.to_str(self)
