"""
Module for utility blender mesh methods
"""

from typing import List, Tuple

import bmesh
import bpy
from bmesh.types import BMesh
from mathutils import Vector


# METHODS =====================================================================
# Binary ----------------------------------------------------------------------
def create(
        name: str,
        vertices: List[Vector] = None,
        edges: List[Vector] = None,
        faces: List[Vector] = None
) -> BMesh:
    mesh = bpy.data.meshes.new(name)
    if (vertices and len(vertices) > 0) \
            or (edges and len(edges) > 0) \
            or (faces and len(faces) > 0):
        mesh.from_pydata(vertices or [], edges or [], faces or [])
        mesh.update()
    return mesh


def update(mesh: bpy.types.Mesh, bm: BMesh):
    """Update bpy.types.Mesh with BMesh"""
    if bm.is_wrapped:
        bmesh.update_edit_mesh(mesh, False, False)
    else:
        bm.to_mesh(mesh)
        mesh.update()


def edit(mesh: bpy.types.Mesh) -> BMesh:
    """Create BMesh from bpy.types.Mesh"""
    if mesh.is_editmode:
        bm = bmesh.from_edit_mesh(mesh)
    else:
        bm = bmesh.new()
        bm.from_mesh(mesh)
    return bm


# bpy.types.Material --------------------------------------------------------------------
def get_or_create_material(mesh: bpy.types.Mesh, name: str) -> Tuple[bpy.types.Material, int]:
    material = mesh.materials.get(name)
    if not material:
        material = bpy.data.materials.get(name)
        mesh.materials.append(material)
    return material, mesh.materials.keys().index(name)
