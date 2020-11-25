"""
Module for edgs methods relative to plane drawing
"""

from typing import List, Optional

import bmesh

import utils
from model import CartographyGroup
from ..model import CartographyPlaneContext
from . import face as face_utils

# METHODS =====================================================================
def create(
        context: CartographyPlaneContext,
        vert1: bmesh.types.BMVert,
        vert2: bmesh.types.BMVert,
        group: CartographyGroup
) -> Optional[bmesh.types.BMEdge]:
    try:
        edge = context.bmesh.edges.new([vert1, vert2])  # noqa
    except ValueError:
        context.logger.warning('Edge between vertices <%s> and <%s> already exists. Not added to edges list')
        return None

    edges = utils.collection.dict.get_or_create(context.edges_by_group, group, [])
    edges.append(edge)

    if vert1 in context.outline_vertices or vert2 in context.outline_vertices:
        context.outline_edges.append(edge)
    if vert1 in context.gate_vertices and vert2 in context.gate_vertices:
        context.gate_edges.append(edge)

    z1 = edge.verts[0].co.z
    z2 = edge.verts[1].co.z
    if z1 != z2:
        context.logger.warning('The edge <%s> has multiple z axis: v1=<%d> v2=<%d> (Ignored)', str(edge), z1, z2)
    else:
        z_edges = utils.collection.dict.get_or_create(context.edges_by_z, z1, [])
        z_edges.append(edge)

    return edge


def level(
        context: CartographyPlaneContext,
        edges: List[bmesh.types.BMEdge],
        z: float,
        top_face: bool = False,
        mat_index: int = None
):
    context.logger.debug('Level <%d> with z=<%d>', len(edges), z)
    bm = context.bmesh

    # Extrude edges
    extruded = utils.blender.meshing.bmesh_extrude(bm, edges)

    translate_vertices = [v for v in extruded if isinstance(v, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, vec=(0, 0, z), verts=translate_vertices)  # noqa

    # Apply material for extruded faces
    if mat_index is not None:
        created_faces = [v for v in extruded if isinstance(v, bmesh.types.BMFace)]
        for face in created_faces:
            face.material_index = mat_index

    # Create faces of extrude part
    if top_face:
        translate_edges = [e for e in extruded if isinstance(e, bmesh.types.BMEdge)]
        face_utils.create(context, translate_edges)
