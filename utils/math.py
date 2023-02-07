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
def create_vector(x, y, z):
    return Vector((x, y, z))


def distance_3d(loc1: Location, loc2: Location) -> float:
    """Distance between two point in 3D"""
    return math.sqrt(
        math.pow(abs(__get_x(loc1.x) - __get_x(loc2.x)), 2)
        + math.pow(abs(__get_y(loc1.y) - __get_y(loc2.y)), 2)
        + math.pow(abs(__get_z(loc1.z) - __get_z(loc2.z)), 2)
    )


def calc_coordinates_by_dist(p: Vector, dist: int, inverse_y: bool) -> Vector:
    # Formula: round((-distS1²+distS2²-distS1S2²) / (-2 * distS1S2))
    x = round((-math.pow(p.x, 2) + math.pow(p.y, 2) - math.pow(dist, 2)) / (-2 * dist))

    # Formula: distS2 == distS1S2 ? distS1 : round(sqrt(distS2²-(distS1S2-x)²))
    y = p.x if p.y == dist else round(math.sqrt(math.pow(p.y, 2) - math.pow(dist - x, 2)))
    if inverse_y:
        y = -y

    # Formula:  !z ? 0 : z
    z = 0 if not p.z else p.z

    return Vector((x, y, z))


def centroid(locations: List[Location]):
    locations_count = len(locations)
    return (
        sum([__get_x(loc) for loc in locations]) / locations_count,
        sum([__get_y(loc) for loc in locations]) / locations_count,
        sum([__get_z(loc) for loc in locations]) / locations_count
    )


def sum_vector(loc1: Location, loc2: Location) -> Vector:
    """Summary of vectors"""
    return Vector((
        __get_x(loc1) + __get_x(loc2),
        __get_y(loc1) + __get_y(loc2),
        __get_z(loc1) + __get_z(loc2)
    ))


def diff_vector(loc1: Location, loc2: Location) -> Vector:
    """Difference of vectors"""
    return Vector((
        __get_x(loc1) - __get_x(loc2),
        __get_y(loc1) - __get_y(loc2),
        __get_z(loc1) - __get_z(loc2)
    ))


def translate(loc: Location, vector: Location) -> Vector:
    return Vector((
        __get_x(loc) + __get_x(vector),
        __get_y(loc) + __get_y(vector),
        __get_z(loc) + __get_z(vector)
    ))


def same_2d_position(loc1: Location, loc2: Location) -> bool:
    return __get_x(loc1) == __get_x(loc2) and __get_y(loc1) == __get_y(loc2)


def same_3d_position(loc1: Location, loc2: Location) -> bool:
    return __get_x(loc1) == __get_x(loc2) and __get_y(loc1) == __get_y(loc2) and __get_z(loc1) == __get_z(loc2)


# Internal --------------------------------------------------------------------
def __get_x(loc: Location) -> int or float:
    return loc.x if isinstance(loc, Vector) else loc[0]


def __get_y(loc: Location) -> int or float:
    return loc.y if isinstance(loc, Vector) else loc[1]


def __get_z(loc: Location) -> int or float:
    return loc.z if isinstance(loc, Vector) else loc[2]
