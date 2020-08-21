"""
Module for utility methods

History:
2020/08/21: v0.0.1
    + add utility methods for bmesh/mesh conversion
    + add utility methods for matching
"""

import os
import re
import sys

import bmesh
import bpy


# METHODS =====================================================================
# Blender - Meshing -----------------------------------------------------------
def bmesh_from_mesh(mesh: bpy.types.Mesh) -> bmesh.types.BMesh:
    """Create BMesh from Mesh"""
    if mesh.is_editmode:
        bm = bmesh.from_edit_mesh(mesh)
    else:
        bm = bmesh.new()
        bm.from_mesh(mesh)
    return bm


def bmesh_to_mesh(bm: bmesh.types.BMesh, mesh: bpy.types.Mesh):
    """Update Mesh with BMesh"""
    if bm.is_wrapped:
        bmesh.update_edit_mesh(mesh, False, False)
    else:
        bm.to_mesh(mesh)
        mesh.update()


# Path ------------------------------------------------------------------------
def workspace() -> os.path:
    # FIXME ok for debug only
    paths = [path for path in sys.path if os.path.basename(path) == 'blender-cartography-addon']
    return paths[0]


# String - Match --------------------------------------------------------------
def match_around(pattern: str, value: str, flags=0) -> bool:
    return re.match(pattern, value, flags) is not None \
           or re.match(pattern + '.*', value, flags) is not None \
           or re.match('.*' + pattern + '.*', value, flags) is not None
