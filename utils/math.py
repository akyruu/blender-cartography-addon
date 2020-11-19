"""
Module for utility math methods
"""

import math

from mathutils import Vector


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

    # Formula: distS2 == distS1S2 ? distS1 : round(sqrt(distS2²-(distS1S2-x)²))
    y = p.x if p.y == dist else round(math.sqrt(math.pow(p.y, 2) - math.pow(dist - x, 2)))
    if inverse_y:
        y = -y

    # Formula:  !z ? 0 : z
    z = 0 if not p.z else p.z

    return Vector((x, y, z))
