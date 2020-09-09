"""
Module for drawing

History:
2020/08/21: v0.0.1
    + add cartography drawing
    + add cartography room drawing (point + plane)
"""

import logging
from abc import abstractmethod
from enum import Enum
from typing import Dict, List, Optional

import bmesh
import bpy
from mathutils import Vector

import bca_config
import bca_utils
import mappings
from bca_types import CartographyGroup, CartographyObjectType, CartographyPoint, CartographyCategory, \
    CartographyCategoryType, CartographyRoom
from templating import CartographyTemplate


# Classes =====================================================================
class CartographyDrawer:
    """Drawer of cartography"""

    # Fields ------------------------------------------------------------------
    __logger = logging.getLogger('CartographyDrawer')

    # Constructor -------------------------------------------------------------
    def __init__(self, template: CartographyTemplate, *room_drawers):
        self.__template = template
        self.__room_drawers = room_drawers

    # Methods -----------------------------------------------------------------
    # Draw
    def draw(self, room: CartographyRoom):
        collection = self.__create_collection(room.name)
        for roomDrawer in self.__room_drawers:
            roomDrawer.draw(room, collection)

    # Tools
    def __create_collection(self, name: str) -> bpy.types.Collection:
        collection = bpy.data.collections.get(name)
        if collection is not None:
            self.__logger.debug('Collection <%s> already exists: complete delete', name)
            self.__remove_collection(collection)

        self.__logger.debug('Create a new collection: <%s>', name)
        collection = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(collection)
        return collection

    def __remove_collection(self, collection: bpy.types.Collection):
        # FIXME remove objects in collection not working (remove template object too)
        # objects = [object for object in collection.objects \
        #         if object.users == 1 and object not in self.__template.objects]
        # while objects:
        #     bpy.data.objects.remove(objects.pop())
        bpy.data.collections.remove(collection)


class CartographyRoomDrawer:
    """Abstract drawer of room for cartography"""

    # Fields ------------------------------------------------------------------
    __logger = logging.getLogger('CartographyRoomDrawer')

    # Constructor -------------------------------------------------------------
    def __init__(self, template: CartographyTemplate):
        self._template = template

    # Methods -----------------------------------------------------------------
    # Draw
    @abstractmethod
    def draw(self, room: CartographyRoom, collection: bpy.types.Collection):
        pass

    # Tools
    @staticmethod
    def _create_object(name: str, location: Vector, template: bpy.types.Object, collection: bpy.types.Collection) \
            -> bpy.types.Object:
        obj = template.copy()
        obj.name = name
        obj.location = location
        collection.objects.link(obj)
        return obj

    def _get_template_object(self, enum: Enum, enum_type: str) -> bpy.types.Object:
        template = self._template.objects.get(enum, None)
        if template is None:
            self.__logger.warning('Template not found for %s <%s>', enum_type, enum.name)
        return template


class CartographyStructuralPointDrawer(CartographyRoomDrawer):
    """Drawer of structural points in room for cartography"""

    # Fields ------------------------------------------------------------------
    __logger = logging.getLogger('CartographyStructuralPointDrawer')

    # Constructor -------------------------------------------------------------
    def __init__(self, template):
        CartographyRoomDrawer.__init__(self, template)

    # Methods -----------------------------------------------------------------
    # Draw
    def draw(self, room: CartographyRoom, collection: bpy.types.Collection):
        for point in [p for p in room.all_points if
                      not p.copy and p.category.type == CartographyCategoryType.STRUCTURAL]:
            self.__draw_point(point, collection)

    def __draw_point(self, point: CartographyPoint, collection):
        template = self._get_template_object(point.category, 'category')
        if template is None:
            return
        self._create_object(point.name, point.location, template, collection)


class CartographyInterestPointDrawer(CartographyRoomDrawer):
    """Drawer of interest points in room for cartography"""

    # Fields ------------------------------------------------------------------
    __logger = logging.getLogger('CartographyInterestPointDrawer')

    # Constructor -------------------------------------------------------------
    def __init__(self, template):
        CartographyRoomDrawer.__init__(self, template)

    # Methods -----------------------------------------------------------------
    # Draw
    def draw(self, room: CartographyRoom, collection: bpy.types.Collection):
        for point in [p for p in room.all_points if p.category.type == CartographyCategoryType.INTEREST]:
            if point.category == CartographyCategory.ANTHROPOGENIC_OBJECT:
                self.__draw_anthropogenic_object(point, collection)
            else:
                self.__draw_other(point, collection)

    def __draw_anthropogenic_object(self, point: CartographyPoint, collection: bpy.types.Collection):
        # Check point
        if point.interest is None:
            self.__logger.warning('An interest required for anthropic object point type: %s (Ignored)', str(point))
            return

        # Get template
        template = self._get_template_object(point.interest[0], 'interest type')
        if template is None:
            return

        # Create objects
        z = point.location.z
        for i in range(point.interest[1]):
            obj = self._create_object(point.name, Vector((point.location.x, point.location.y, z)), template, collection)
            z += obj.dimensions.z  # noqa
        return

    def __draw_other(self, point: CartographyPoint, collection: bpy.types.Collection):
        # Get template and create point
        template = self._get_template_object(point.category, 'category')
        if template is None:
            return
        obj = self._create_object(point.name, point.location, template, collection)

        # Icon
        if point.interest is not None:
            # Get icon template
            template = self._get_template_object(point.interest[0], 'interest type')
            if template is None:
                return

            # Create image
            name = obj.name + '_icon'
            z = obj.location.z + obj.dimensions.z  # noqa
            self._create_object(name, Vector((obj.location.x, obj.location.y, z)), template, collection)  # noqa


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
        obj = self._create_object(name, Vector((0, 0, 0)), template, collection)

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
        self.__mesh = bca_utils.obj_get_mesh(obj)
        self.__mat_wall_index = self.__get_or_create_material(mappings.cartography_mat_wall)
        self.__mat_climbing_index = self.__get_or_create_material(mappings.cartography_mat_climbing)

        # Get bmesh instance
        bm = self.__bmesh = bca_utils.bmesh_from_mesh(self.__mesh)

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
                z0_edge = bca_utils.list_next(e for e in z0_edges if self.__one_edge_above_the_other(e, edge))
                if z0_edge:
                    self.__level_edges([z0_edge], z, False, self.__mat_climbing_index if z == 1 else None)

        # Level outline edges
        outline_edges = [e for e in self.__outline_edges if e not in self.__gate_edges]
        max_z = max(self.__edges_by_z.keys()) + bca_config.outline_z
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
        bca_utils.bmesh_to_mesh(self.__bmesh, self.__mesh)

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

        vertices = bca_utils.dict_get_or_create(self.__vertices_by_group, group, [])
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

        edges = bca_utils.dict_get_or_create(self.__edges_by_group, group, [])
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
            z_edges = bca_utils.dict_get_or_create(self.__edges_by_z, z1, [])
            z_edges.append(edge)

        return edge

    def __create_faces(self, edges: List[bmesh.types.BMEdge]):
        fill = bmesh.ops.triangle_fill(self.__bmesh, use_beauty=True, use_dissolve=False, edges=edges)  # noqa
        return [g for g in fill['geom'] if isinstance(g, bmesh.types.BMFace)]

    def __level_edges(self, edges: List[bmesh.types.BMEdge], z: float, top_face: bool = False, mat_index: int = None):
        self.__logger.debug('Level <%d> with z=<%d>', len(edges), z)
        bm = self.__bmesh

        # Extrude edges
        extruded = bca_utils.bmesh_extrude(bm, edges)

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


# [UN]REGISTER ================================================================
__classes__ = (
    # CartographyDrawer,
    # CartographyRoomDrawer,
    # CartographyPointDrawer,
    # CartographyPlaneDrawer,
)
