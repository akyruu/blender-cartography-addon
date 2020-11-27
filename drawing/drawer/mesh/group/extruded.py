"""
Module for extruded of mesh group drawer
"""

import logging
from typing import List

from bmesh.types import BMEdge, BMFace, BMesh, BMVert

import mappings
import utils
from utils.blender.bmesh import Geometry
from .common import CartographyMeshGroupContext, CartographyMeshGroupDrawer


# CLASSES =====================================================================
class CartographyMeshExtrudedGroupDrawer(CartographyMeshGroupDrawer):
    """Drawer of mesh for cartography extruded group"""

    # Fields ------------------------------------------------------------------
    __logger = logging.getLogger('CartographyMeshExtrudedGroupDrawer')

    # Constructor -------------------------------------------------------------
    def __init__(self, ):
        CartographyMeshGroupDrawer.__init__(self)

        self._extruded_material_index: int = 0

        self._to_level_edges: List[BMEdge] = []
        self._translate_edges: List[BMEdge] = []

    # Methods -----------------------------------------------------------------
    # Reset
    def _reset(self, context: CartographyMeshGroupContext):  # overridden
        CartographyMeshGroupDrawer._reset(self, context)

        self._extruded_material_index = context.get_or_create_material(mappings.cartography_mat_wall)

        self._to_level_edges = []
        self._translate_edges = []

    # Edges
    def _draw_edges(self, context: CartographyMeshGroupContext):  # overridden
        treated = 0
        count = len(self._vertices)
        for i in range(1, count):
            if treated:
                treated -= 1
                continue

            prev_vertex = self._vertices[i - 1]
            curr_vertex = self._vertices[i]
            if (not utils.blender.bmesh.vert.same_2d_position(prev_vertex, curr_vertex)) \
                    and prev_vertex.co.z != curr_vertex.co.z \
                    and i < (count - 2):
                next_vertex_1 = self._vertices[i + 1]
                next_vertex_2 = self._vertices[i + 2]
                if (prev_vertex.co.z == next_vertex_1.co.z and curr_vertex.co.z == next_vertex_2.co.z) \
                        or (utils.blender.bmesh.vert.same_2d_position(curr_vertex, next_vertex_1)):
                    self._create_edge(context.bm, prev_vertex, next_vertex_1)
                    self._create_edge(context.bm, next_vertex_1, curr_vertex)
                    self._create_edge(context.bm, curr_vertex, next_vertex_2)
                    treated = 2
                    continue
            self._create_edge(context.bm, prev_vertex, curr_vertex)

        # Close
        if count > 1:
            self._close_edge(context.bm, self._vertices)

    def _close_edge(self, bm: BMesh, vertices: List[BMVert]):
        self._create_edge(bm, vertices[len(vertices) - 1], vertices[0])

    def _create_edge(self, bm: BMesh, vert1: BMVert, vert2: BMVert, based=True, append=True) -> BMEdge:  # overridden
        edge = CartographyMeshGroupDrawer._create_edge(self, bm, vert1, vert2, based)
        if append:
            if self._is_edge_to_level(edge):
                self._to_level_edges.append(edge)
        return edge

    def _is_edge_to_level(self, edge: BMEdge) -> bool:
        vert1, vert2 = edge.verts
        return not utils.blender.bmesh.vert.same_2d_position(vert1, vert2)

    # Faces
    def _draw_faces(self, context: CartographyMeshGroupContext) -> List[BMFace]:  # overridden
        group_category = context.group.category
        self._draw_wall_face(context.bm, group_category.level)
        if group_category.ground:
            self._draw_ground_face(context)

        return self._faces

    # Faces - Wall
    def _draw_wall_face(self, bm: BMesh, height: int):
        self._translate_edges = []

        z_levels = self._get_z_levels(height)
        for edge in self._to_level_edges:
            vert1, vert2 = edge.verts
            if vert1.co.z != vert2.co.z:
                edge = self._extrude_not_regular_edge(bm, edge)
            translate_edge = self._extrude_regular_edge(bm, edge, z_levels)
            self._translate_edges.append(translate_edge)

    def _get_z_levels(self, z_max_level: int) -> List[int]:
        negative = z_max_level < 0

        z_limit = 0
        z_comp = min if negative else max

        z_levels = []
        for vertex in self._vertices:
            z = vertex.co.z
            z_limit = z_comp(z_limit, z)
            if vertex.co.z not in z_levels:
                z_levels.append(z)

        z_levels.sort()
        if negative:
            z_levels.reverse()
        z_levels.append(z_limit + z_max_level)

        return z_levels

    def _extrude_not_regular_edge(self, bm: BMesh, edge: BMEdge) -> BMEdge:
        vert1, vert2 = edge.verts
        if vert1.co.z < vert2.co.z:
            vert1, vert2 = vert2, vert1
        vert3 = utils.blender.bmesh.vert.new(bm, (vert2.co.x, vert2.co.y, vert1.co.z))
        level_edge = utils.blender.bmesh.edge.new(bm, vert1, vert3)
        close_edge = utils.blender.bmesh.edge.new(bm, vert2, vert3)

        faces = self._create_faces(bm, [edge, level_edge, close_edge])
        utils.blender.bmesh.face.apply_material(faces, self._extruded_material_index)

        return level_edge

    def _extrude_regular_edge(self, bm: BMesh, edge: BMEdge, z_levels: List[int]) -> BMEdge:
        z = edge.verts[0].co.z

        z_limit = z_levels[len(z_levels) - 1]
        for z_level in [zl for zl in z_levels if (zl < z if z_limit < 0 else zl > z)]:
            extruded = self._extrude_edge_z(bm, edge, z_level - z)
            utils.blender.bmesh.face.apply_material(extruded.faces, self._extruded_material_index)

            edge = utils.collection.list.inext(e for e in extruded.edges if e.verts[0].co.z == e.verts[1].co.z)
            z = z_level

        return edge

    # Faces - Ground
    def _draw_ground_face(self, context: CartographyMeshGroupContext):
        ground_edges = self._get_ground_edges(context)
        return self._create_faces(context.bm, ground_edges)

    def _get_ground_edges(self, context: CartographyMeshGroupContext) -> List[BMEdge]:
        return self._translate_edges

    # Faces - Tools
    def _create_faces(self, bm: BMesh, edges: List[BMEdge]) -> List[BMFace]:
        faces = utils.blender.bmesh.face.new(bm, edges)
        self._faces += faces
        return faces

    def _extrude_edge_z(self, bm: BMesh, edge: BMEdge, height: int) -> Geometry:
        # FIXME use manual extrusion for fix errors for draw the outline ground
        # extruded = utils.blender.bmesh.ops.extrude_edges_z(bm, [edge], height)

        vert1a, vert1b = edge.verts
        vert2a = self._create_vertex_internal(bm, (vert1a.co.x, vert1a.co.y, vert1a.co.z + height))
        vert2b = self._create_vertex_internal(bm, (vert1b.co.x, vert1b.co.y, vert1b.co.z + height))

        edge1a1b = edge
        edge1a2a = self._create_edge_internal(bm, vert1a, vert2a)
        edge1b2b = self._create_edge_internal(bm, vert1b, vert2b)
        edge2a2b = self._create_edge_internal(bm, vert2a, vert2b)
        edges = [edge1a1b, edge1a2a, edge2a2b, edge1b2b]

        faces = utils.blender.bmesh.face.new(bm, edges)
        extruded = Geometry([vert2a, vert2b, edge1a2a, edge1b2b, edge2a2b] + faces)  # noqa
        # FIXME end
        self._faces += extruded.faces
        return extruded
