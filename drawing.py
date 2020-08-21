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

import bmesh
import bpy

import bca_utils
from bca_types import CartographyObjectType, CartographyPoint, CartographyPointCategory, CartographyPointCategoryType, \
    CartographyRoom
from templating import CartographyTemplate


# __classes__ =====================================================================
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
    def draw(self, rooms):
        for room in rooms:
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
    def draw(self, room: CartographyRoom, collection):
        pass

    # Tools
    @staticmethod
    def _create_object(name: str, x: int, y: int, z: int, template: bpy.types.Object, collection: bpy.types.Collection):
        obj = template.copy()
        obj.name = name
        obj.location.x = x
        obj.location.y = y
        obj.location.z = z
        collection.objects.link(obj)
        return obj

    def _get_template_object(self, enum: Enum, enum_type: str) -> bpy.types.Object:
        template = self._template.objects.get(enum, None)
        if template is None:
            self.__logger.warning('Template not found for %s <%s>', enum_type, enum.name)
        return template


class CartographyPointDrawer(CartographyRoomDrawer):
    """Drawer of points in room for cartography"""

    # Fields ------------------------------------------------------------------
    __logger = logging.getLogger('CartographyPointDrawer')

    # Constructor -------------------------------------------------------------
    def __init__(self, template):
        CartographyRoomDrawer.__init__(self, template)

    # Methods -----------------------------------------------------------------
    # Draw
    def draw(self, room: CartographyRoom, collection):
        for point in room.points:
            self.__draw_point(point, collection)

    def __draw_point(self, point: CartographyPoint, collection):
        # Get template and create point
        template = self._get_template_object(point.category, 'category')
        if template is None:
            return
        obj = self._create_object(point.name, point.x, point.y, point.z, template, collection)

        # Icon
        if point.interest_type is not None:
            # Get icon template
            template = self._get_template_object(point.interest_type, 'interest type')
            if template is None:
                return

            # Create image
            name = obj.name + '_icon'
            z = obj.location.z + obj.dimensions.z
            self._create_object(name, obj.location.x, obj.location.y, z, template, collection)


class CartographyPlaneDrawer(CartographyRoomDrawer):
    """Drawer of points in room for cartography"""

    # Fields ------------------------------------------------------------------
    __logger = logging.getLogger('CartographyPointDrawer')

    # Constructor -------------------------------------------------------------
    def __init__(self, template):
        CartographyRoomDrawer.__init__(self, template)

        self.__mesh = None
        self.__bmesh = None

        self.__verticesByCategory = {}
        self.__outlineVertices = []

        self.__edgesByCategory = {}
        self.__outlineEdges = []

    # Methods -----------------------------------------------------------------
    # Draw
    def draw(self, room: CartographyRoom, collection):
        # Get template
        template = self._get_template_object(CartographyObjectType.PLANE, 'object type')
        if template is None:
            return

        # Create object
        name = room.name + '_plane'
        point = room.points[0]
        obj = self._create_object(name, 0, 0, 0, template, collection)

        # Update mesh
        self.__update_mesh(room, obj)

    def __update_mesh(self, room: CartographyRoom, obj):
        self.__logger.debug('Update mesh for room <%s>', room.name)
        self.__update_mesh_init(obj)
        self.__update_mesh_create_vertices(room)
        self.__update_mesh_create_edges()
        self.__update_mesh_create_faces()
        self.__update_mesh_level_edges()
        self.__update_mesh_apply()

    def __update_mesh_init(self, obj):
        self.__logger.debug('Update mesh initialization...')
        # Get mesh instance
        self.__mesh = obj.data
        bm = self.__bmesh = bca_utils.bmesh_from_mesh(self.__mesh)

        # Delete all vertices
        bmesh.ops.delete(bm, geom=bm.verts)

        # Work variables
        self.__verticesByCategory = {}
        self.__outlineVertices = []
        self.__edgesByCategory = {}
        self.__outlineEdges = []
        for category in iter(CartographyPointCategory):
            self.__verticesByCategory[category] = []
            self.__edgesByCategory[category] = []

    def __update_mesh_create_vertices(self, room: CartographyRoom):
        self.__logger.debug('Update mesh - create vertices...')
        points = [point for point in room.points \
                  if point.category is not None and point.category.type == CartographyPointCategoryType.STRUCTURAL]
        for point in points:
            self.__logger.debug('Update mesh for point <%s>', point.name)
            self.__create_vertex(point.x, point.y, 0, point.category)

    def __update_mesh_create_edges(self):
        self.__logger.debug('Update mesh - create edges...')

        # Create not outline edges
        vertices_by_category = self.__verticesByCategory
        for category in [c for c in vertices_by_category if not c.outline]:
            vertices = vertices_by_category.get(category)
            count = len(vertices)
            if count > 1:
                self.__logger.debug('Update mesh - create <%d> edges for category <%s>...', count, category.name)
                for i in range(1, count):
                    self.__create_edge(vertices[i - 1], vertices[i], category)

                # Close polygon
                if count > 2:
                    self.__logger.debug('Update mesh - close polygon for category <%s>...', category.name)
                    self.__create_edge(vertices[-1], vertices[0], category)

        # Create outline edges
        vertices = self.__outlineVertices
        gate_vertices = vertices_by_category.get(CartographyPointCategory.GATE)
        count = len(vertices)
        if count > 1:
            self.__logger.debug('Update mesh - create <%d> edges for outline...', count)
            for i in range(1, count):
                prev_vertice = vertices[i - 1]
                curr_vertice = vertices[i]
                category = CartographyPointCategory.GATE \
                    if prev_vertice in gate_vertices and curr_vertice in gate_vertices \
                    else CartographyPointCategory.OUTLINE
                self.__create_edge(prev_vertice, curr_vertice, category)

            # Close polygon
            if count > 2:
                self.__logger.debug('Update mesh - close polygon for outline...')
                self.__create_edge(vertices[-1], vertices[0], category)

    def __update_mesh_create_faces(self):
        self.__logger.debug('Update mesh - create faces...')
        self.__create_faces(self.__bmesh.edges)

    # TODO apply rock_cliff on vertical faces
    def __update_mesh_level_edges(self):
        self.__logger.debug('Update mesh - level edges...')

        # Level outline edges
        gate_edges = self.__edgesByCategory.get(CartographyPointCategory.GATE)
        outline_edges = [e for e in self.__outlineEdges if e not in gate_edges]
        self.__level_edges(outline_edges)

        # Level edges specific categories        
        for category in self.__edgesByCategory:
            edges = self.__edgesByCategory.get(category)
            if not category.outline and category.level and len(edges) > 2:  # TODO <= 2 case
                self.__level_edges(edges, category.level, category.face)

    def __update_mesh_apply(self):
        self.__logger.debug('Update mesh apply...')
        bca_utils.bmesh_to_mesh(self.__bmesh, self.__mesh)

    # Method - Tools
    def __create_vertex(self, x: int, y: int, z: int, category: CartographyPointCategory):
        vertex = self.__bmesh.verts.new((x, y, z))

        vertices = self.__verticesByCategory.get(category)
        vertices.append(vertex)

        if category.outline:
            self.__outlineVertices.append(vertex)

        return vertex

    def __create_edge(self, vertice1: bmesh.types.BMVert, vertice2: bmesh.types.BMVert,
                      category: CartographyPointCategory):
        edge = self.__bmesh.edges.new([vertice1, vertice2])

        edges = self.__edgesByCategory.get(category)
        edges.append(edge)

        if category.outline:
            self.__outlineEdges.append(edge)

        return edge

    def __create_faces(self, edges):
        fill = bmesh.ops.triangle_fill(self.__bmesh, use_beauty=True, use_dissolve=False, edges=edges)
        return [g for g in fill['geom'] if isinstance(g, bmesh.types.BMFace)]

    def __level_edges(self, edges, z=1, face=False):
        self.__logger.debug('Level <%d> with z=<%d>', len(edges), z)
        bm = self.__bmesh

        # Extrude edges
        extruded = bmesh.ops.extrude_face_region(bm, geom=edges)
        extruded_geom = extruded['geom']

        translate_verts = [v for v in extruded_geom if isinstance(v, bmesh.types.BMVert)]
        bmesh.ops.translate(bm, vec=(0, 0, z), verts=translate_verts)

        # Create faces of extrude part
        if face:
            translate_edges = [e for e in extruded_geom if isinstance(e, bmesh.types.BMEdge)]
            self.__create_faces(translate_edges)


# [UN]REGISTER ================================================================
__classes__ = (
    # CartographyDrawer,
    # CartographyRoomDrawer,
    # CartographyPointDrawer,
    # CartographyPlaneDrawer,
)
