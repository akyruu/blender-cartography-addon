"""
Module for utility math methods
"""

import math

from mathutils import Vector


# METHODS =====================================================================
def math_3d_distance(p1: Vector, p2: Vector) -> float:
    return math.sqrt(
        math.pow(abs(p1.x - p2.x), 2)
        + math.pow(abs(p1.y - p2.y), 2)
        + math.pow(abs(p1.z - p2.z), 2)
    )
