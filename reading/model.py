"""
Module for common methods relative to reading
"""

import os
from enum import Enum
from logging import Logger
from typing import List, Optional

from mathutils import Vector

import utils


# CLASSES =====================================================================
class CartographyFile:
    """Cartography file"""

    # Constructor -------------------------------------------------------------
    def __init__(self, filepath: os.path):
        self.path = filepath
        self.headers: List[CartographyFileLine] = []
        self.info: Optional[CartographyFileInfo] = None
        self.points: List[CartographyFilePoint] = []

    # Methods -----------------------------------------------------------------
    def __repr__(self):
        return utils.object.to_repr(self)

    def __str__(self):
        return utils.object.to_str(self)


class CartographyFileLine:
    """Line in cartography file"""

    # Constructor -------------------------------------------------------------
    def __init__(self, row: int, text: str):
        self.row = row
        self.text = text

    # Methods -----------------------------------------------------------------
    def __repr__(self):
        return utils.object.to_repr(self)

    def __str__(self):
        return utils.object.to_str(self)


class CartographyFileInfo(CartographyFileLine):
    """Cartography file info"""

    # Constructor -------------------------------------------------------------
    def __init__(self, row: int, text: str):
        CartographyFileLine.__init__(self, row, text)
        self.scribes1: List[str] = []
        self.scribes2: List[str] = []
        self.explorers: List[str] = []
        self.s1s2_distance = 0

    # Methods -----------------------------------------------------------------
    def __repr__(self):
        return utils.object.to_repr(self)

    def __str__(self):
        return utils.object.to_str(self)


class CartographyFileSide(Enum):
    """Side of point line in cartography file"""
    LEFT = 1
    RIGHT = 2
    UNKNOWN = 3


class CartographyFilePoint(CartographyFileLine):
    """Point line in cartography file"""

    # Constructor -------------------------------------------------------------
    def __init__(
            self,
            row: int,
            text: str,
            location: Vector = Vector((0, 0, 0)),
            observations: List[str] = (),
            point_name: str = '',
            side: CartographyFileSide = None,
            s1_distance: int = 0,
            s2_distance: int = 0,
            height: int = 0,
    ):
        CartographyFileLine.__init__(self, row, text)
        self.location = location
        self.observations = observations
        self.point_name = point_name
        self.side = side
        self.s1_distance = s1_distance
        self.s2_distance = s2_distance
        self.height = height

    # Methods -----------------------------------------------------------------
    def __repr__(self):
        return utils.object.to_repr(self)

    def __str__(self):
        return utils.object.to_str(self)


class ReadContext:
    """Context for CartographyReader"""

    def __init__(self, separator: str, logger: Logger):
        self.separator = separator
        self.row: int = 1
        self.column: int = 1
        self.logger: Logger = logger
