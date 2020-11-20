"""
Module for plane drawer
"""

import logging
from typing import Dict, List, Optional

import bmesh
import bpy
from mathutils import Vector

import config
import mappings
import utils
from model import CartographyGroup, CartographyObjectType, CartographyCategory, \
    CartographyCategoryType, CartographyRoom
from templating import CartographyTemplate
from .common import CartographyRoomDrawer


# Classes =====================================================================
class CartographyPlaneDrawer(CartographyRoomDrawer):
    """Drawer of points in room for cartography"""

    # Fields ------------------------------------------------------------------
    __logger = logging.getLogger('CartographyPointDrawer')

    # Constructor -------------------------------------------------------------
    def __init__(self, template: CartographyTemplate):
        CartographyRoomDrawer.__init__(self, template)

        self.__mesh: Optional[bpy.types.Mesh] = None
        self.__mat_wall_index = None
        self.__mat_climbing_index = None
        self.__bmesh: Optional[bmesh.types.BMesh] = None

        self.__vertices_by_group: Dict[CartographyGroup, List[bmesh.types.BMVert]] = {}
        self.__gate_vertices: List[bmesh.types.BMVert] = []
        self.__outline_vertices: List[bmesh.types.BMVert] = []

        self.__edges_by_group: Dict[CartographyGroup, List[bmesh.types.BMEdge]] = {}
        self.__edges_by_z: Dict[float, List[bmesh.types.BMEdge]] = {}
        self.__gate_edges: List[bmesh.types.BMEdge] = []
        self.__outline_edges: List[bmesh.types.BMEdge] = []

    # Methods -----------------------------------------------------------------
    # Draw
    def draw(self, room: CartographyRoom, collection: bpy.types.Collection):
        # Get template
        template = self._get_template_object(CartographyObjectType.PLANE, 'object type')
        if template is None:
            return

        # Create object
        name = room.name + '_plane'
        obj = utils.blender.object.create(name, Vector((0, 0, 0)), template, collection)

        # Update mesh
        self.__update_mesh(room, obj)

    def __update_mesh(self, room: CartographyRoom, obj: bpy.types.Object):
        self.__logger.debug('Update mesh for room <%s>', room.name)
        self.__update_mesh_init(obj)
        self.__update_mesh_create_vertices(room)
        self.__update_mesh_create_edges()
        self.__update_mesh_create_faces()
        self.__update_mesh_level_edges()
        self.__update_mesh_end()
        self.__update_mesh_apply()

    def __update_mesh_init(self, obj: bpy.types.Object):
        self.__logger.debug('Update mesh initialization...')

        # Get mesh instance
        self.__mesh = utils.blender.meshing.obj_get_mesh(obj)
        self.__mat_wall_index = self.__get_or_create_material(mappings.cartography_mat_wall)
        self.__mat_climbing_index = self.__get_or_create_material(mappings.cartography_mat_climbing)

        # Get bmesh instance
        bm = self.__bmesh = utils.blender.meshing.bmesh_from_mesh(self.__mesh)

        # Delete all vertices
        bmesh.ops.delete(bm, geom=bm.verts)  # noqa

        # Work variables
        self.__vertices_by_group = {}
        self.__gate_vertices = []
        self.__outline_vertices = []
        self.__edges_by_group = {}
        self.__edges_by_z = {}
        self.__gate_edges = []
        self.__outline_edges = []

    def __update_mesh_create_vertices(self, room: CartographyRoom):
        self.__logger.debug('Update mesh - create vertices...')
        for point, group in [
            (p, g) for g in room.groups.values() for p in g.points
            if g.category is not None and g.category.type == CartographyCategoryType.STRUCTURAL
        ]:
            self.__logger.debug('Update mesh for point <%s>', point.name)
            self.__create_vertex(point.location, group, point.category)

    def __update_mesh_create_edges(self):
        self.__logger.debug('Update mesh - create edges...')

        # Create edges by group
        vertices_by_group = self.__vertices_by_group
        for group, vertices in [(g, verts) for g, verts in vertices_by_group.items()]:
            count = len(vertices)

            # Create edge between vertices
            self.__logger.debug('Update mesh - create <%d> edges for group <%s>...', count, group.name)
            for i in range(1, count):
                self.__create_edge(vertices[i - 1], vertices[i], group)

            # Close polygon
            if count > 2:
                self.__logger.debug('Update mesh - close polygon for group <%s>...', group.name)
                self.__create_edge(vertices[-1], vertices[0], group)

    def __update_mesh_create_faces(self):
        self.__logger.debug('Update mesh - create faces...')

        # Create faces by z axis
        for z, edges in self.__edges_by_z.items():
            self.__logger.debug('Update mesh - create faces for z axis <%d>...', z)
            self.__create_faces(edges)

    # TODO apply rock_cliff on vertical faces
    def __update_mesh_level_edges(self):
        self.__logger.debug('Update mesh - level edges...')

        # Level edges between z axis for edge under another
        z0_edges = self.__edges_by_z.get(0)  # FIXME update for use another of 0 level
        if not z0_edges:
            self.__logger.warning('No edges found for z=0')
        else:
            for z, edge in [(z, e) for z, edges in self.__edges_by_z.items() for e in edges if z != 0]:
                z0_edge = utils.collection.list.inext(e for e in z0_edges if self.__one_edge_above_the_other(e, edge))
                if z0_edge:
                    self.__level_edges([z0_edge], z, False, self.__mat_climbing_index if z == 1 else None)

        # Level outline edges
        outline_edges = [e for e in self.__outline_edges if e not in self.__gate_edges]
        max_z = max(self.__edges_by_z.keys()) + config.outline_z
        for z, edges in self.__edges_by_z.items():
            edges = [e for e in edges if e in outline_edges]
            if len(edges) > 0:
                self.__level_edges(edges, max_z - z, False, self.__mat_wall_index)

        # Level edges specific categories
        for group, edges in [
            (g, e) for g, e in self.__edges_by_group.items()
            if not g.category.outline and g.category.level and len(e) > 2
        ]:
            self.__level_edges(edges, group.category.level, group.category.top_face, self.__mat_wall_index)

    def __update_mesh_end(self):
        bm = self.__bmesh
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.001)

    def __update_mesh_apply(self):
        self.__logger.debug('Update mesh apply...')
        utils.blender.meshing.bmesh_to_mesh(self.__bmesh, self.__mesh)

    # Method - Tools
    def __get_or_create_material(self, mat_name: str) -> int:
        material = self.__mesh.materials.get(mat_name)
        if not material:
            material = bpy.data.materials.get(mat_name)
            self.__mesh.materials.append(material)
        return self.__mesh.materials.values().index(material)

    def __create_vertex(self, vec: Vector, group: CartographyGroup, category: CartographyCategory = None) \
            -> bmesh.types.BMVert:
        vertex = self.__bmesh.verts.new(vec)  # noqa

        vertices = utils.collection.dict.get_or_create(self.__vertices_by_group, group, [])
        vertices.append(vertex)

        category = category if category else group.category
        if category.outline:
            self.__outline_vertices.append(vertex)
        if category == CartographyCategory.GATE:
            self.__gate_vertices.append(vertex)

        return vertex

    def __create_edge(self, vert1: bmesh.types.BMVert, vert2: bmesh.types.BMVert, group: CartographyGroup) \
            -> bmesh.types.BMEdge:
        edge = self.__bmesh.edges.new([vert1, vert2])  # noqa

        edges = utils.collection.dict.get_or_create(self.__edges_by_group, group, [])
        edges.append(edge)

        if vert1 in self.__outline_vertices or vert2 in self.__outline_vertices:
            self.__outline_edges.append(edge)
        if vert1 in self.__gate_vertices and vert2 in self.__gate_vertices:
            self.__gate_edges.append(edge)

        z1 = edge.verts[0].co.z
        z2 = edge.verts[1].co.z
        if z1 != z2:
            self.__logger.warning('The edge <%s> has multiple z axis: v1=<%d> v2=<%d> (Ignored)', str(edge), z1, z2)
        else:
            z_edges = utils.collection.dict.get_or_create(self.__edges_by_z, z1, [])
            z_edges.append(edge)

        return edge

    def __create_faces(self, edges: List[bmesh.types.BMEdge]):
        fill = bmesh.ops.triangle_fill(self.__bmesh, use_beauty=True, use_dissolve=False, edges=edges)  # noqa
        return [g for g in fill['geom'] if isinstance(g, bmesh.types.BMFace)]

    def __level_edges(self, edges: List[bmesh.types.BMEdge], z: float, top_face: bool = False, mat_index: int = None):
        self.__logger.debug('Level <%d> with z=<%d>', len(edges), z)
        bm = self.__bmesh

        # Extrude edges
        extruded = utils.blender.meshing.bmesh_extrude(bm, edges)

        translate_verts = [v for v in extruded if isinstance(v, bmesh.types.BMVert)]
        bmesh.ops.translate(bm, vec=(0, 0, z), verts=translate_verts)  # noqa

        # Apply material for extruded faces
        if mat_index is not None:
            created_faces = [v for v in extruded if isinstance(v, bmesh.types.BMFace)]
            for face in created_faces:
                face.material_index = mat_index

        # Create faces of extrude part
        if top_face:
            translate_edges = [e for e in extruded if isinstance(e, bmesh.types.BMEdge)]
            self.__create_faces(translate_edges)

    @staticmethod
    def __one_edge_above_the_other(edge1: bmesh.types.BMEdge, edge2: bmesh.types.BMEdge):
        return edge1.verts[0].co.x == edge2.verts[0].co.x and edge1.verts[0].co.y == edge2.verts[0].co.y \
               and edge1.verts[1].co.x == edge2.verts[1].co.x and edge1.verts[1].co.y == edge2.verts[1].co.y
