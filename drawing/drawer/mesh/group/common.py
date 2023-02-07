"""
Module for common of mesh group drawer
"""

import logging
from abc import abstractmethod
from typing import Dict, List, Optional, Tuple

import bpy
import utils
from bmesh.types import BMEdge, BMFace, BMesh, BMVert
from model import CartographyGroup, CartographyPoint, CartographyRoom
from utils.blender.bmesh import Geometry
from utils.math import Location

# TYPES =======================================================================
CartographyMeshGroupEdge = Tuple[BMVert, BMVert, bool]


# CLASSES =====================================================================
class CartographyMeshGroupGeometry(Geometry):
    """Specific implementation of common Geometry for CartographyMeshGroupDrawer"""

    # Constructor -------------------------------------------------------------
    def __init__(self):
        Geometry.__init__(self)
        self.based_edges: List[BMEdge] = []


class CartographyMeshGroupContext:
    """Context of CartographyMeshGroupDrawer"""

    # Constructor -------------------------------------------------------------
    def __init__(self, mesh: bpy.types.Mesh, bm: BMesh, room: CartographyRoom):
        self.mesh = mesh
        self.bm = bm

        self.room = room
        self.group: Optional[CartographyGroup] = None

        self.geom_by_group: Dict[str, CartographyMeshGroupGeometry] = {}
        self.outline_geom: Optional[CartographyMeshGroupGeometry] = None

    # Methods -----------------------------------------------------------------
    def get_or_create_material(self, name: str) -> int:
        material, index = utils.blender.mesh.get_or_create_material(self.mesh, name)
        return index


class CartographyMeshGroupDrawer:
    """Drawer of mesh for cartography group"""

    # Fields ------------------------------------------------------------------
    __logger = logging.getLogger('CartographyMeshGroupDrawer')

    # Constructor -------------------------------------------------------------
    def __init__(self):
        self._vertices: List[BMVert] = []
        self._edges: List[BMEdge] = []
        self._based_edges: List[BMEdge] = []
        self._faces: List[BMFace] = []

    # Methods -----------------------------------------------------------------
    def draw(self, context: CartographyMeshGroupContext) -> CartographyMeshGroupGeometry:
        # Reset and draw group
        self._reset(context)
        self._draw_vertices(context)
        self._draw_edges(context)
        self._draw_faces(context)

        # Build geometry to return
        geom = CartographyMeshGroupGeometry()
        geom.append_all(self._vertices)
        geom.append_all(self._edges)
        geom.based_edges = self._based_edges
        geom.faces = self._faces
        return geom

    # Reset
    def _reset(self, context: CartographyMeshGroupContext):
        self._vertices = []
        self._edges = []
        self._based_edges = []
        self._faces = []

    # Vertices
    def _draw_vertices(self, context: CartographyMeshGroupContext):
        for point in context.group.points:
            self._create_vertex(context.bm, point)

    def _create_vertex(self, bm: BMesh, point: CartographyPoint, append=True) -> BMVert:
        vertex = self._create_vertex_internal(bm, point.location)
        if append:
            if vertex in self._vertices:
                raise Exception(f'[{point.name}] Duplicated vertex: <{vertex.co}>')
            self._vertices.append(vertex)
        return vertex

    def _create_vertex_internal(self, bm: BMesh, location: Location) -> BMVert:
        vertex = utils.blender.bmesh.vert.get(bm, location)
        if not vertex:
            self.__logger.debug('Create vertex: <%s>', str(location))
            vertex = utils.blender.bmesh.vert.new(bm, location)
        else:
            self.__logger.debug('No create vertex. Already exists in mesh: <%s>', str(location))
        return vertex

    # Edges
    @abstractmethod
    def _draw_edges(self, context: CartographyMeshGroupContext):
        pass

    def _create_edge(self, bm: BMesh, vert1: BMVert, vert2: BMVert, based: bool, append=True) -> BMEdge:
        edge = self._create_edge_internal(bm, vert1, vert2)
        if append:
            if edge in self._edges:
                raise Exception(f'Duplicated edge: <{[v.co for v in edge.verts]}>')
            self._edges.append(edge)
            if based:
                if edge in self._based_edges:
                    raise Exception(f'Duplicated based edge: <{[v.co for v in edge.verts]}>')
                self._based_edges.append(edge)
        return edge

    def _create_edge_internal(self, bm: BMesh, vert1: BMVert, vert2: BMVert) -> BMEdge:
        edge = utils.blender.bmesh.edge.get(bm, [vert1, vert2])
        if not edge:
            self.__logger.debug('Create edge: <%s>', str([vert1.co, vert2.co]))
            edge = utils.blender.bmesh.edge.new(bm, vert1, vert2)
        else:
            self.__logger.debug('No create edge. Already exists in mesh: <%s>', str([vert1.co, vert2.co]))
        return edge

    # Faces
    @abstractmethod
    def _draw_faces(self, context: CartographyMeshGroupContext):
        pass
