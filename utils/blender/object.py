"""
Module for utility blender object methods
"""

import bpy
from bpy.types import Collection, Mesh, Object
from mathutils import Vector


# METHODS =====================================================================
def create(name: str, location: Vector, template: Object, collection: Collection) \
        -> bpy.types.Object:
    obj = template.copy()
    obj.name = name
    obj.location = location
    collection.objects.link(obj)
    return obj


def get_mesh(obj: Object) -> Mesh:
    return obj.data  # noqa
