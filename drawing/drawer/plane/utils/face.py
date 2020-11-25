"""
Module for face methods relative to plane drawing
"""

from typing import List

import bmesh

from ..model import CartographyPlaneContext


# METHODS =====================================================================
def create(context: CartographyPlaneContext, edges: List[bmesh.types.BMEdge]):
    fill = bmesh.ops.triangle_fill(context.bmesh, use_beauty=True, use_dissolve=False, edges=edges)  # noqa
    return [g for g in fill['geom'] if isinstance(g, bmesh.types.BMFace)]
