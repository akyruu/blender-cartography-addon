"""
Module for utility math methods
"""

import math
from typing import List, Tuple

from mathutils import Vector

# TYPES =======================================================================
Location = Vector or Tuple[float, float, float] or Tuple[int, int, int]
BiLocation = Tuple[Location] or List[Location]


# METHODS =====================================================================
def distance_3d(p1: Vector, p2: Vector) -> float:
    return math.sqrt(
        math.pow(abs(p1.x - p2.x), 2)
        + math.pow(abs(p1.y - p2.y), 2)
        + math.pow(abs(p1.z - p2.z), 2)
    )


def calc_coordinates_by_dist(p: Vector, dist: int, inverse_y: bool) -> Vector:
    # Formula: round((-distS1²+distS2²-distS1S2²) / (-2 * distS1S2))
    x = round((-math.pow(p.x, 2) + math.pow(p.y, 2) - math.pow(dist, 2)) / (-2 * dist))
    print('######### calc_coordinates_by_dist: x=(', -math.pow(p.x, 2), '+', math.pow(p.y, 2), '-', math.pow(dist, 2),
          ') /', (-2 * dist), '=', x)

    # Formula: distS2 == distS1S2 ? distS1 : round(sqrt(distS2²-(distS1S2-x)²))
    y = p.x if p.y == dist else round(math.sqrt(math.pow(p.y, 2) - math.pow(dist - x, 2)))
    if inverse_y:
        y = -y

    # Formula:  !z ? 0 : z
    z = 0 if not p.z else p.z

    return Vector((x, y, z))


def same_2d_position(loc1: Location, loc2: Location) -> bool:
    return __get_x(loc1) == __get_x(loc2) and __get_y(loc1) == __get_y(loc2)


def same_3d_position(loc1: Location, loc2: Location) -> bool:
    return __get_x(loc1) == __get_x(loc2) and __get_y(loc1) == __get_y(loc2) and __get_z(loc1) == __get_z(loc2)


def __get_x(loc: Location) -> int or float:
    return loc.x if isinstance(loc, Vector) else loc[0]


def __get_y(loc: Location) -> int or float:

    return loc.y if isinstance(loc, Vector) else loc[1]


def __get_z(loc: Location) -> int or float:
    return loc.z if isinstance(loc, Vector) else loc[2]
