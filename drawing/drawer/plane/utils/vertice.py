"""
Module for vertice methods relative to plane drawing
"""

import bmesh
from mathutils import Vector

import utils
from model import CartographyGroup, CartographyCategory
from ..model import CartographyPlaneContext


# METHODS =====================================================================
def create(
        context: CartographyPlaneContext,
        vector: Vector,
        group: CartographyGroup,
        category: CartographyCategory = None
) -> bmesh.types.BMVert:
    vertice = context.bmesh.verts.new(vector)  # noqa

    vertices = utils.collection.dict.get_or_create(context.vertices_by_group, group, [])
    vertices.append(vertice)

    category = category if category else group.category
    if category.outline:
        context.outline_vertices.append(vertice)
    if category == CartographyCategory.GATE:
        context.gate_vertices.append(vertice)

    return vertice
