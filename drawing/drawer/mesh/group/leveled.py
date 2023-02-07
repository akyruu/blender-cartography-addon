"""
Module for leveled of mesh group drawer
"""

import logging
from typing import Callable, List

import config
import utils
from bmesh.types import BMEdge, BMFace, BMesh, BMVert
from model import CartographyCategory, CartographyGroup, CartographyPoint
from utils.blender.bmesh import Geometry
from .common import CartographyMeshGroupContext, CartographyMeshGroupDrawer
from .... import config as draw_config


# TODO check algo for negative leveled (based on z negative ?
# CLASSES =====================================================================
class CartographyMeshLeveledGroupDrawer(CartographyMeshGroupDrawer):
    """Drawer of mesh for cartography leveled group"""

    # Fields ------------------------------------------------------------------
    __logger = logging.getLogger('CartographyMeshLeveledGroupDrawer')

    # Constructor -------------------------------------------------------------
    def _init__(self):
        CartographyMeshGroupDrawer.__init__(self)

        self._leveled_material_index: int = 0
        self._climbing_material_index: int = 0

        self._outline_vertices: List[BMVert] = []
        self._top_vertices: List[BMVert] = []
        self._bottom_vertices: List[BMVert] = []

        self._outline_top_edges: List[BMEdge] = []
        self._faced_edges: List[List[BMEdge]] = []
        self._top_edges: List[BMEdge] = []
        self._bottom_edges: List[BMEdge] = []

    # Methods -----------------------------------------------------------------
    # Reset
    def _reset(self, context: CartographyMeshGroupContext):  # overridden
        CartographyMeshGroupDrawer._reset(self, context)

        self._leveled_material_index = context.get_or_create_material(draw_config.template.material_wall)
        self._climbing_material_index = context.get_or_create_material(draw_config.template.material_climbing)

        self._outline_vertices = []
        self._top_vertices = []
        self._bottom_vertices = []

        self._outline_top_edges = []
        self._faced_edges = []
        self._top_edges = []
        self._bottom_edges = []

    # Vertices
    def _create_vertex(self, bm: BMesh, point: CartographyPoint, append=True) -> BMVert:
        vertex = CartographyMeshGroupDrawer._create_vertex(self, bm, point)
        if point.has_category(CartographyCategory.OUTLINE):
            self._outline_vertices.append(vertex)

        # Add (or replace) the top/bottom vertices for same 2D position
        self._append_vertex_to_limits(vertex, self._top_vertices, lambda vertex_z, top_z: vertex_z > top_z)
        self._append_vertex_to_limits(vertex, self._bottom_vertices, lambda vertex_z, bottom_z: vertex_z < bottom_z)

        return vertex

    @staticmethod
    def _append_vertex_to_limits(vertex: BMVert, limit_vertices: List[BMVert], comp: Callable[[float, float], bool]):
        limit_vertex = next((v for v in limit_vertices if utils.blender.bmesh.vert.same_2d_position(v, vertex)), None)
        if not limit_vertex:
            limit_vertices.append(vertex)
        elif comp(vertex.co.z, limit_vertex.co.z):
            limit_vertices.remove(limit_vertex)
            limit_vertices.append(vertex)

    # Edges
    def _draw_edges(self, context: CartographyMeshGroupContext):  # overridden
        vertices_by_2d_position = self._group_vertices_by_2d_position()
        count = len(vertices_by_2d_position)

        # Create geometry
        for i in range(1, count):
            self._draw_faced_edges(context.bm, vertices_by_2d_position, i - 1, i)

        # Close geometry
        if count > 1:
            self._draw_faced_edges(context.bm, vertices_by_2d_position, 0, count - 1)

        # Fixes
        self._fix_outline_top_edges(context.bm, context.group, context.outline_geom)

    def _group_vertices_by_2d_position(self):
        vertices_by_2d_position: List[List[BMVert]] = []

        # Build groups
        vertices: List[BMVert] = []
        for v in self._vertices:
            if vertices and not utils.blender.bmesh.vert.same_2d_position(v, vertices[-1]):
                vertices.sort(key=lambda v0: v0.co.z)
                vertices_by_2d_position.append(vertices)
                vertices = []
            vertices.append(v)

        # Add last group if not empty
        if vertices:
            vertices.sort(key=lambda v0: v0.co.z)
            vertices_by_2d_position.append(vertices)

        return vertices_by_2d_position

    def _draw_faced_edges(self, bm: BMesh, vertices_by_2d_position: List[List[BMVert]], start_index, end_index):
        start_vertices = vertices_by_2d_position[start_index]
        end_vertices = vertices_by_2d_position[end_index].copy()
        end_vertices.reverse()
        vertices = start_vertices + end_vertices
        self._create_faced_edges(bm, vertices)

    def _create_faced_edges(self, bm: BMesh, vertices: List[BMVert]) -> List[BMEdge]:
        faced_edges = []

        # Check if faced edges not corresponding to outline
        if utils.collection.list.contains_all(self._outline_vertices, vertices):
            self.__logger.debug('Faced edges outlined: %s', str([v.co for v in vertices]))

            top_vert1, top_vert2 = [v for v in vertices if v in self._top_vertices]
            self.__logger.debug('Create only the top edge: [%s, %s]', str(top_vert1.co), str(top_vert2.co))
            edge = self._get_or_create_faced_edge(bm, top_vert1, top_vert2)
            self._outline_top_edges.append(edge)
        else:
            count = len(vertices)
            if count > 2:
                # Create face
                self.__logger.debug('Create faced edges: %s', str([v.co for v in vertices]))

                for i in range(1, count):
                    edge = self._get_or_create_faced_edge(bm, vertices[i - 1], vertices[i])
                    faced_edges.append(edge)

                # Close face
                edge = self._get_or_create_faced_edge(bm, vertices[count - 1], vertices[0])
                faced_edges.append(edge)

                self._faced_edges.append(faced_edges)
            else:
                # Create a single edge
                self.__logger.debug('Create single edge: %s', str([v.co for v in vertices]))
                self._get_or_create_faced_edge(bm, vertices[0], vertices[1])

        return faced_edges

    def _get_or_create_faced_edge(self, bm: BMesh, vert1: BMVert, vert2: BMVert) -> BMEdge:
        edge = next((e for e in self._edges if utils.blender.bmesh.edge.same_3d_position(e, (vert1, vert2))), None)
        if not edge:
            edge = self._create_edge(bm, vert1, vert2)
        return edge

    def _fix_outline_top_edges(self, bm: BMesh, group: CartographyGroup, outline_geom: Geometry):
        """Fix when a leveled group is in junction with outline"""
        if self._outline_top_edges:
            start_edge = self._outline_top_edges[0]
            end_edge = self._outline_top_edges[len(self._outline_top_edges) - 1]

            start_vert = start_edge.verts[0]  # noqa
            end_vert = end_edge.verts[1]  # noqa
            ground_outline_edges = utils.collection.list.find_sublist(
                outline_geom.edges,
                lambda e: utils.blender.bmesh.vert.same_3d_position(e.verts[0], start_vert),
                (lambda e: utils.blender.bmesh.vert.same_3d_position(e.verts[1], end_vert), 1)
            )

            count = len(self._outline_top_edges)
            outline_count = len(ground_outline_edges)
            if ground_outline_edges and outline_count != count:
                self.__logger.info(
                    'Replace outline edges for ground of group: <%s> (%d -> %d)',
                    group.name, count, outline_count
                )
                start = self._top_edges.index(start_edge)
                utils.collection.list.remove_values(self._top_edges, self._outline_top_edges)
                utils.blender.bmesh.edge.remove_all(bm, self._outline_top_edges)
                utils.collection.list.insert_values(self._top_edges, start, ground_outline_edges)
                self._outline_top_edges = ground_outline_edges
            else:
                self.__logger.debug('Keep outline edges for ground of group: <%s>', group.name)

    def _create_edge(self, bm: BMesh, vert1: BMVert, vert2: BMVert, based=False, append=True) -> BMEdge:  # overridden
        is_top = vert1 in self._top_vertices and vert2 in self._top_vertices
        is_bottom = vert1 in self._bottom_vertices and vert2 in self._bottom_vertices

        edge = CartographyMeshGroupDrawer._create_edge(self, bm, vert1, vert2, is_bottom, append)
        if is_top:
            self._top_edges.append(edge)
        elif is_bottom:
            self._bottom_edges.append(edge)
        return edge

    # Faces
    def _draw_faces(self, context: CartographyMeshGroupContext) -> List[BMFace]:  # overridden
        for edges in self._faced_edges:
            self._draw_wall_face(context.bm, edges)
        self._draw_ground_face(context)
        return self._faces

    def _draw_wall_face(self, bm: BMesh, edges: List[BMEdge]):
        faces = self._create_faces(bm, edges)

        # Calculate max height
        max_height = 0
        for face in faces:
            max_height = max(utils.blender.bmesh.face.calc_z_height(face), max_height)

        # Determine and apply material
        material_index = self._climbing_material_index \
            if max_height <= config.common.max_climbing_height \
            else self._leveled_material_index
        utils.blender.bmesh.face.apply_material(faces, material_index)

    def _draw_ground_face(self, context: CartographyMeshGroupContext):
        ground_edges = self._get_ground_edges(context)
        ground_edges_count = len(ground_edges)
        if ground_edges_count < 3:
            # TODO raise an exception and intercept in parent call ???
            self.__logger.debug(f'Failed to draw ground face: insufficient edges {ground_edges_count} < 3. Ignored')
            return

        self._create_faces(context.bm, ground_edges)

    def _get_ground_edges(self, context: CartographyMeshGroupContext) -> List[BMEdge]:
        edges = self._top_edges
        for linked_group in context.group.linked:
            linked_name = linked_group.name
            linked_geom = context.geom_by_group.get(linked_name)
            if linked_geom:
                self.__logger.debug('Linked geometry found <%s> for group <%s>', linked_name, context.group.name)
                edges += linked_geom.based_edges
            else:
                self.__logger.warning('Geometry not found for linked group: <%s>', linked_name)

        return edges

    def _create_faces(self, bm: BMesh, edges: List[BMEdge]) -> List[BMFace]:
        faces = utils.blender.bmesh.face.new(bm, edges)
        self._faces += faces
        return faces
