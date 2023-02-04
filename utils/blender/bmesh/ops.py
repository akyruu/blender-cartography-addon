"""
Module for utility blender mesh methods
"""

from typing import List, Union

import bmesh
from bmesh.types import BMEdge, BMFace, BMesh, BMVert

from .common import Geometry


# METHODS =====================================================================
def clean(bm: BMesh):
    bmesh.ops.delete(bm, geom=bm.verts, context='VERTS')


def extrude(bm: BMesh, geom: List[Union[BMVert, BMEdge, BMFace]]) -> Geometry:
    """Extrude a geometry and return vertices, edges and faces created"""
    prev_faces = [f for f in bm.faces]
    extruded = bmesh.ops.extrude_face_region(bm, geom=geom)
    extruded_geom = extruded['geom']

    # FIXME Add missing faces created in extruded geom for some reason
    if len(bm.faces) > len(prev_faces):
        extruded_geom += [f for f in bm.faces if f not in prev_faces]

    return Geometry(extruded_geom)


def extrude_z(bm: BMesh, geom: List[Union[BMVert, BMEdge, BMFace]], z: float or int) -> Geometry:
    extruded = extrude(bm, geom)
    bmesh.ops.translate(bm, vec=(0, 0, z), verts=extruded.vertices)  # noqa
    return extruded
