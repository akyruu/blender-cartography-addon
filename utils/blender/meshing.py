"""
Module for utility blender meshing methods
"""

from typing import List, Union

import bmesh
import bpy
from mathutils import Vector


# METHODS =====================================================================
def bmvert_global_coordinate(vert: bmesh.types.BMVert, obj: bpy.types.Object) -> Vector:
    """Get global coordinate for a vertex"""
    return obj.matrix_world @ vert.co  # noqa


def bmesh_extrude(
        bm: bmesh.types.BMesh,
        geom: List[Union[bmesh.types.BMVert, bmesh.types.BMEdge, bmesh.types.BMFace]]
) -> List[Union[bmesh.types.BMVert, bmesh.types.BMEdge, bmesh.types.BMFace]]:
    """Extrude a geometry and return vertices, edges and faces created"""
    prev_faces = [f for f in bm.faces]
    extruded = bmesh.ops.extrude_face_region(bm, geom=geom)
    extruded_geom = extruded['geom']

    # FIXME Add missing faces created in extruded geom for some reason
    if len(bm.faces) > len(prev_faces):
        extruded_geom += [f for f in bm.faces if f not in prev_faces]

    return extruded_geom


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


def obj_get_mesh(obj: bpy.types.Object) -> bpy.types.Mesh:
    return obj.data  # noqa
