"""
Module for extruded of mesh group drawer
"""

import logging
from typing import List

from bmesh.types import BMEdge, BMFace, BMesh, BMVert

from drawing import config as draw_config
from utils.blender import bmesh as bmesh_utils
from utils.blender.bmesh import Geometry
from utils.collection import list as list_utils
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

        self._extruded_material_index = context.get_or_create_material(draw_config.template.material_wall)

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
            if (not bmesh_utils.vert.same_2d_position(prev_vertex, curr_vertex)) \
                    and prev_vertex.co.z != curr_vertex.co.z \
                    and i < (count - 2):
                next_vertex_1 = self._vertices[i + 1]
                next_vertex_2 = self._vertices[i + 2]
                if (prev_vertex.co.z == next_vertex_1.co.z and curr_vertex.co.z == next_vertex_2.co.z) \
                        or (bmesh_utils.vert.same_2d_position(curr_vertex, next_vertex_1)):
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
        return not bmesh_utils.vert.same_2d_position(vert1, vert2)

    # Faces
    def _draw_faces(self, context: CartographyMeshGroupContext) -> List[BMFace]:  # overridden
        group_category = context.group.category

        height = group_category.options.level
        vert_z_list = [v.co.z for v in self._vertices]
        limit_z = min(vert_z_list) if height < 0 else max(vert_z_list)
        self._draw_wall_face(context.bm, limit_z + height)

        if group_category.options.ground:
            self._draw_ground_face(context)

        return self._faces

    # Faces - Wall
    def _draw_wall_face(self, bm: BMesh, z: int):
        for edge in self._to_level_edges:
            extruded = self._extrude_edge_z(bm, edge, z)
            bmesh_utils.face.apply_material(extruded.faces, self._extruded_material_index)
            translate_edge = list_utils.inext(e for e in extruded.edges if e.verts[0].co.z == e.verts[1].co.z)
            self._translate_edges.append(translate_edge)

    # FIXME merge this code with the creation of faced edges ?
    def _extrude_edge_z(self, bm: BMesh, edge: BMEdge, z: int) -> Geometry:
        # FIXME use manual extrusion for fix errors for draw the outline ground
        # extruded = utils.blender.bmesh.ops.extrude_edges_z(bm, [edge], height)

        # Create faced vertices
        vert1a, vert1b = edge.verts
        vert2a = self._create_vertex_internal(bm, (vert1a.co.x, vert1a.co.y, z))
        vert2b = self._create_vertex_internal(bm, (vert1b.co.x, vert1b.co.y, z))

        vertices_a = self._build_vertical_edge(vert1a, vert2a)
        vertices_b = self._build_vertical_edge(vert2b, vert1b)  # Reverse for keep junction between A edges and B edges
        vertices = vertices_a + vertices_b

        # Create faced edges
        edges = []
        for i in range(1, len(vertices)):
            edges.append(self._create_edge_internal(bm, vertices[i - 1], vertices[i]))
        edges.append(edge)  # Close face

        faces = bmesh_utils.face.new(bm, edges)
        extruded = Geometry(
            verts=[v for v in vertices if v not in edge.verts],
            edges=[e for e in edges if e != edge],
            faces=faces
        )
        # FIXME end
        self._faces += extruded.faces
        return extruded

    def _build_vertical_edge(self, vert1: BMVert, vert2: BMVert) -> List[BMVert]:
        neg = vert2.co.z < vert1.co.z
        comp = (lambda v: vert1.co.z > v.co.z > vert2.co.z) if neg else (lambda v: vert1.co.z < v.co.z < vert2.co.z)
        vertices = [v for v in self._vertices if bmesh_utils.vert.same_2d_position(v, vert1) and comp(v)]
        vertices.sort(key=lambda v: v.co.z)
        if neg:
            vertices.reverse()
        return [vert1] + vertices + [vert2]

    # Faces - Ground
    def _draw_ground_face(self, context: CartographyMeshGroupContext):
        ground_edges = self._get_ground_edges(context)
        return self._create_faces(context.bm, ground_edges)

    def _get_ground_edges(self, context: CartographyMeshGroupContext) -> List[BMEdge]:
        return self._translate_edges

    # Faces - Tools
    def _create_faces(self, bm: BMesh, edges: List[BMEdge]) -> List[BMFace]:
        faces = bmesh_utils.face.new(bm, edges)
        self._faces += faces
        return faces
