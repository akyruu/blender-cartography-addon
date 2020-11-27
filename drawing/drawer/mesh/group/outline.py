"""
Module for outline of mesh group drawer
"""

import logging
from typing import Dict, List, Optional, Tuple

from bmesh.types import BMEdge, BMesh, BMVert

from model import CartographyCategory, CartographyGroup, CartographyPoint, CartographyRoom
from utils.blender import bmesh as bmesh_utils
from utils.collection import list as list_utils, dict as dict_utils
from .common import CartographyMeshGroupContext, CartographyMeshGroupGeometry
from .extruded import CartographyMeshExtrudedGroupDrawer


# CLASSES =====================================================================
class CartographyMeshOutlineGroupDrawer(CartographyMeshExtrudedGroupDrawer):
    """Drawer of mesh for cartography outline group"""

    # Fields ------------------------------------------------------------------
    __logger = logging.getLogger('CartographyMeshOutlineGroupDrawer')

    # Constructor -------------------------------------------------------------
    def __init__(self):
        CartographyMeshExtrudedGroupDrawer.__init__(self)
        self.__gate_vertices: List[BMVert] = []
        self.__group: Optional[CartographyGroup] = None

    # Methods -----------------------------------------------------------------
    # Reset
    def _reset(self, context: CartographyMeshGroupContext):  # override
        CartographyMeshExtrudedGroupDrawer._reset(self, context)
        self.__gate_vertices = []
        self.__group = context.group

    # Vertices
    def _create_vertex(self, bm: BMesh, point: CartographyPoint, append=True) -> BMVert:  # overridden
        vertex = CartographyMeshExtrudedGroupDrawer._create_vertex(self, bm, point, append)
        if point.category == CartographyCategory.GATE:
            self.__gate_vertices.append(vertex)
        return vertex

    # Edges
    def _close_edge(self, bm: BMesh, vertices: List[BMVert]):
        vert1 = vertices[0]
        if vert1 in self.__gate_vertices:
            reverse_vertices = vertices.copy()
            reverse_vertices.reverse()

            vert2: Optional[BMVert] = None
            for i in range(0, len(reverse_vertices)):
                vert = reverse_vertices[i]
                if vert in self.__gate_vertices:
                    if not vert2 or vert.co.z > vert2.co.z:
                        vert2 = vert
                elif vert2:
                    break
        else:
            vert2 = vertices[len(vertices) - 1]

        self._create_edge(bm, vert2, vert1)

    def _is_edge_to_level(self, edge: BMEdge):  # overridden
        return CartographyMeshExtrudedGroupDrawer._is_edge_to_level(self, edge) \
               and not self.__is_gate_edge(edge)

    def __is_gate_edge(self, edge: BMEdge):
        vert1, vert2 = edge.verts
        return vert1 in self.__gate_vertices and vert2 in self.__gate_vertices

    # Faces - Ground
    def _draw_ground_face(self, context: CartographyMeshGroupContext):  # overridden
        # The ground must be draw at the end (after all others structural forms)
        pass

    def draw_ground_face(self, context: CartographyMeshGroupContext):
        """Delayed draw of ground face to the end (after all others structural geometries)"""
        CartographyMeshExtrudedGroupDrawer._draw_ground_face(self, context)

    def _get_ground_edges(self, context: CartographyMeshGroupContext) -> List[BMEdge]:  # overridden
        edges = self._edges
        junction, standalone = self.__split_geoms(context.room, context.geom_by_group)

        # Insert junction geometries
        for group_name, geom in junction.items():
            self.__insert_junction_edges(edges, group_name, geom)

        # Add standalone geometries at the end
        for group_name, geom in standalone.items():
            edges += geom.based_edges

        return edges

    def __split_geoms(self, room: CartographyRoom, geom_by_group: Dict[str, CartographyMeshGroupGeometry]) \
            -> Tuple[Dict[str, CartographyMeshGroupGeometry], Dict[str, CartographyMeshGroupGeometry]]:
        junction = {}
        standalone = {}

        # Filter geoms
        filtered_geom_by_group = geom_by_group.copy()
        for group_name, geom in geom_by_group.items():
            group = room.groups.get(group_name)
            linked_names = [g.name for g in group.linked]
            if linked_names:
                self.__logger.debug('Delete linked geometry to group <%s>: <%s>', group_name, str(linked_names))
                dict_utils.pop_all(filtered_geom_by_group, linked_names)

        # Split filtered geoms
        for group_name, geom in filtered_geom_by_group.items():  # Outline group isn't in this dictionary
            group = room.groups.get(group_name)
            geoms = junction if room.has_junction(group, self.__group) else standalone
            geoms[group_name] = geom

        return junction, standalone

    def __insert_junction_edges(self, edges: List[BMEdge], group_name: str, geom: CartographyMeshGroupGeometry):
        # Collect edges in junction
        junction_edges = []
        based_edges = geom.based_edges
        for i, edge in enumerate(edges):
            for based_edge in based_edges:
                if bmesh_utils.edge.has_3d_junction(edge, based_edge):
                    junction_edges.append(edge)

        # Remove outline edges in collision and insert based edges of geometry
        if junction_edges:
            start_index = edges.index(junction_edges[0]) + 1
            end_index = edges.index(junction_edges[len(junction_edges) - 1])
            if start_index < end_index:
                self.__logger.debug(
                    'Replace <%d> outline edges by <%d> based edges from group <%s>',
                    end_index - start_index, len(based_edges), group_name
                )
                list_utils.remove_sublist(edges, start_index, end_index)
                list_utils.insert_values(edges, start_index, based_edges)
            else:
                # TODO
                print('TODO')
        else:
            self.__logger.warning('No junction edge found for group <%s>', group_name)
