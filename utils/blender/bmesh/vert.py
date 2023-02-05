"""
Module for utility blender mesh methods
"""

from typing import Tuple

import bpy
from bmesh.types import BMesh, BMVert
from mathutils import Vector
from utils.math import Location
from ... import math as math_utils


# METHODS =====================================================================
def global_co(vert: BMVert, obj: bpy.types.Object) -> Vector:
    """Get global coordinate for a vertex"""
    return obj.matrix_world @ vert.co  # noqa


def get(bm: BMesh, location: Location) -> BMVert:
    vector = Vector(location) if isinstance(location, Tuple) else location
    return next((v for v in bm.verts if math_utils.same_3d_position(v.co, vector)), None)


def new(bm: BMesh, location: Location) -> BMVert:
    return bm.verts.new(location)  # noqa


def same_2d_position(vert1: BMVert or Location, vert2: BMVert or Location) -> bool:
    return math_utils.same_2d_position(__get_location(vert1), __get_location(vert2))


def same_3d_position(vert1: BMVert or Location, vert2: BMVert or Location) -> bool:
    return math_utils.same_3d_position(__get_location(vert1), __get_location(vert2))


def __get_location(vert: BMVert or Location) -> Location:
    return vert.co if isinstance(vert, BMVert) else vert
