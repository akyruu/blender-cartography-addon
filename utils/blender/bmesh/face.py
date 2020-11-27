"""
Module for utility blender mesh methods
"""

import logging
from typing import List

import bmesh
from bmesh.types import BMEdge, BMFace, BMesh

from . import edge as edge_utils

# VARIABLES ===================================================================
__logger = logging.getLogger('blender_bmesh_face')


# METHODS =====================================================================
def new(bm: BMesh, edges: List[BMEdge], use_only_triangle=False) -> List[BMFace]:
    try:
        fill = bmesh.ops.triangle_fill(bm, use_beauty=True, use_dissolve=False, edges=edges)  # noqa
    except ValueError as err:
        return []  # FIXME test
        duplicated_edges = edge_utils.get_duplicated(edges)
        if duplicated_edges:
            raise Exception(
                'Failed to draw faces for edges: <{}>. Edges used multiple times: <{}>',
                [[v.co for v in e.verts] for e in edges],
                [([v.co for v in e.verts], c) for e, c in duplicated_edges]
            )
        raise Exception('Failed to draw faces for edges: <{}>', [[v.co for v in e.verts] for e in edges]) \
            .with_traceback(err.__traceback__)

    if fill['geom']:
        faces = [g for g in fill['geom'] if isinstance(g, BMFace)]
    elif not use_only_triangle:
        __logger.warning('Triangle fill not working. Try to create face manually...')
        vertices = edge_utils.get_vertices(edges)
        faces = [bm.faces.new(vertices)]  # noqa
    else:
        faces = []

    if not faces:
        raise Exception('Failed to create face for vertices: <{}>', str([v.co for v in edge_utils.get_vertices(edges)]))
    return faces


def calc_z_height(face: BMFace) -> float:
    min_z = 0
    max_z = 0
    for vertex in face.verts:
        min_z = min(vertex.co.z, min_z)
        max_z = max(vertex.co.z, max_z)
    return max_z - min_z


def apply_material(faces: List[BMFace], index: int):
    for face in faces:
        face.material_index = index
