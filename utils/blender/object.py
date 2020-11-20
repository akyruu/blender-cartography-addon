"""
Module for utility blender object methods
"""

import bpy
from mathutils import Vector


# METHODS =====================================================================
def create(name: str, location: Vector, template: bpy.types.Object, collection: bpy.types.Collection) \
        -> bpy.types.Object:
    obj = template.copy()
    obj.name = name
    obj.location = location
    collection.objects.link(obj)
    return obj
