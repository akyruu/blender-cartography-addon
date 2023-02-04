"""
Module for utility blender mesh methods
"""

from typing import List, Tuple

import bmesh
import bpy
from bmesh.types import BMesh
from bpy.types import Mesh, Material
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


def update(mesh: Mesh, bm: BMesh):
    """Update Mesh with BMesh"""
    if bm.is_wrapped:
        bmesh.update_edit_mesh(mesh, False, False)
    else:
        bm.to_mesh(mesh)
        mesh.update()


def edit(mesh: Mesh) -> BMesh:
    """Create BMesh from Mesh"""
    if mesh.is_editmode:
        bm = bmesh.from_edit_mesh(mesh)
    else:
        bm = bmesh.new()
        bm.from_mesh(mesh)
    return bm


# Material --------------------------------------------------------------------
def get_or_create_material(mesh: Mesh, name: str) -> Tuple[Material, int]:
    material = mesh.materials.get(name)
    if not material:
        material = bpy.data.materials.get(name)
        mesh.materials.append(material)
    return material, mesh.materials.keys().index(name)
