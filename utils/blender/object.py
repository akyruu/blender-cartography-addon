"""
Module for utility blender object methods
"""

import bpy
from bpy.types import Collection, Mesh, Object

from utils.math import Location


# METHODS =====================================================================
def create_from_template(name: str, location: Location, template: Object, collection: Collection) -> bpy.types.Object:
    obj = template.copy()
    obj.name = name
    obj.location = location
    collection.objects.link(obj)
    return obj


def create_from_mesh(name: str, location: Location, mesh: Mesh, collection: Collection) -> bpy.types.Object:
    obj = bpy.data.objects.new(name, mesh)
    obj.location = location
    collection.objects.link(obj)
    return obj


def get_mesh(obj: Object) -> Mesh:
    return obj.data  # noqa
