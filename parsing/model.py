"""
Module for private entities relative to parsing
"""

from logging import Logger
from typing import Optional, Dict

from model import CartographyGroup, CartographyPoint, CartographyRoom


# CLASSES =====================================================================
class PointGroupTuple:
    """Tuple with point and group"""

    def __init__(self, point: CartographyPoint, group: CartographyGroup):
        self.point = point
        self.group = group


class JunctionGroup:
    """Junction between two points"""

    def __init__(self, room: CartographyRoom, group: CartographyGroup):
        self.room = room
        self.group = group
        self.start: Optional[CartographyParser.__PointGroupTuple] = None  # noqa
        self.end: Optional[CartographyParser.__PointGroupTuple] = None  # noqa


class ParseContext:
    """Context for CartographyParser"""

    def __init__(self, room: CartographyRoom, logger: Logger):
        self.room: CartographyRoom = room
        self.row: int = 0
        self.junctions: Dict[str, JunctionGroup] = {}
        self.logger: Logger = logger
