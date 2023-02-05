"""
Module for utility blender object methods
"""

import bpy

from utils.math import Location


# METHODS =====================================================================
def create_from_template(
        name: str,
        location: Location,
        template: bpy.types.Object,
        collection: bpy.types.Collection
) -> bpy.types.Object:
    obj = template.copy()
    obj.name = name
    obj.location = location
    collection.objects.link(obj)
    return obj


def create_from_mesh(
        name: str,
        location: Location,
        mesh: bpy.types.Mesh,
        collection: bpy.types.Collection
) -> bpy.types.Object:
    obj = bpy.data.objects.new(name, mesh)
    obj.location = location
    collection.objects.link(obj)
    return obj


def get_mesh(obj: bpy.types.Object) -> bpy.types.Mesh:
    return obj.data
