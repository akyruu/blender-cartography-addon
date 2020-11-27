"""
Module for plane drawer
"""

import logging

import bmesh
import bpy
from mathutils import Vector

import config
import mappings
import utils
from drawing.drawer.common import CartographyRoomDrawer
from model import CartographyObjectType, CartographyCategory, CartographyCategoryType, CartographyRoom
from templating import CartographyTemplate
from . import utils as plane_utils
from .model import CartographyPlaneContext


# Classes =====================================================================
class CartographyPlaneDrawer(CartographyRoomDrawer):
    """
    Drawer of points in room for cartography

    TODO split this class in multiple files
    """

    # Fields ------------------------------------------------------------------
    __logger = logging.getLogger('CartographyPointDrawer')

    # Constructor -------------------------------------------------------------
    def __init__(self, template: CartographyTemplate):
        CartographyRoomDrawer.__init__(self, template)
        self.__context = CartographyPlaneContext(template, self.__logger)

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
        self.__context.mesh = utils.blender.object.get_mesh(obj)
        self.__context.mat_wall_index = self.__get_or_create_material(mappings.cartography_mat_wall)
        self.__context.mat_climbing_index = self.__get_or_create_material(mappings.cartography_mat_climbing)

        # Get bmesh instance
        bm = self.__context.bmesh = utils.blender.mesh.edit(self.__context.mesh)

        # Delete all vertices
        bmesh.ops.delete(bm, geom=bm.verts)  # noqa

        # Work variables
        self.__context.vertices_by_group = {}
        self.__context.gate_vertices = []
        self.__context.outline_vertices = []
        self.__context.edges_by_group = {}
        self.__context.edges_by_z = {}
        self.__context.gate_edges = []
        self.__context.outline_edges = []

    def __update_mesh_create_vertices(self, room: CartographyRoom):
        self.__logger.debug('Update mesh - create vertices...')
        for point, group in [
            (p, g) for g in room.groups.values() for p in g.points
            if g.category is not None and g.category.type == CartographyCategoryType.STRUCTURAL
        ]:
            self.__logger.debug('Update mesh for point <%s>', point.name)
            plane_utils.vertice.create(self.__context, point.location, group, point.category)

    def __update_mesh_create_edges(self):
        self.__logger.debug('Update mesh - create edges...')

        # Create edges by group
        vertices_by_group = self.__context.vertices_by_group
        for group, vertices in vertices_by_group.items():
            count = len(vertices)

            # TODO use only one algo not depends on a if for each levels size
            # Determine the number of levels
            levels = 1
            for v in vertices:
                levels = max(len([v0 for v0 in vertices if utils.blender.bmesh.vert.same_2d_position(v0, v)]), levels)
            self.__logger.info('<%d> levels of vertices found for group <%s>', levels, group.name)

            if levels == 2:
                # TODO generalize this algo for all levels number
                vertices_by_level = {}
                for v in vertices:
                    level_vertices = utils.collection.dict.get_or_create(vertices_by_level, v.co.z, [])
                    level_vertices.append(v)

                for level, level_vertices in vertices_by_level.items():
                    count = len(level_vertices)
                    for i in range(1, count):
                        plane_utils.edge.create(self.__context, level_vertices[i - 1], level_vertices[i], group)
                    if count >= 2:
                        plane_utils.edge.create(self.__context, level_vertices[count - 1], level_vertices[0], group)
            else:
                if levels > 2:
                    self.__logger.warning(
                        'Too much levels (%d > 2) for group <%s>. Use default generation of edge',
                        levels, group.name
                    )

                # Create edge between vertices
                self.__logger.debug('Update mesh - create <%d> edges for group <%s>...', count, group.name)
                for i in range(1, count):
                    plane_utils.edge.create(self.__context, vertices[i - 1], vertices[i], group)

                # Close polygon
                if count > 2:
                    self.__logger.debug('Update mesh - close polygon for group <%s>...', group.name)
                    plane_utils.edge.create(self.__context, vertices[-1], vertices[0], group)

    def __update_mesh_create_faces(self):
        self.__logger.debug('Update mesh - create faces...')

        # Create faces by z axis
        for z, edges in self.__context.edges_by_z.items():
            self.__logger.debug('Update mesh - create faces for z axis <%d>...', z)
            plane_utils.face.create(self.__context, edges)

    # TODO apply rock_cliff on vertical faces
    def __update_mesh_level_edges(self):
        self.__logger.debug('Update mesh - level edges...')

        # Level edges between z axis for edge under another
        z0_edges = self.__context.edges_by_z.get(0)  # FIXME update for use another of 0 level
        if not z0_edges:
            self.__logger.warning('No edges found for z=0')
        else:
            for z, edge in [(z, e) for z, edges in self.__context.edges_by_z.items() for e in edges if z != 0]:
                z0_edge = utils.collection.list.inext(e for e in z0_edges if self.__one_edge_above_the_other(e, edge))
                if z0_edge:
                    plane_utils.edge.level(
                        self.__context, [z0_edge], z, False,
                        self.__context.mat_climbing_index if z == 1 else None
                    )

        # Level outline edges
        outline_edges = [e for e in self.__context.outline_edges if e not in self.__context.gate_edges]
        max_z = max(self.__context.edges_by_z.keys()) + CartographyCategory.OUTLINE.level
        for z, edges in self.__context.edges_by_z.items():
            edges = [e for e in edges if e in outline_edges]
            if len(edges) > 0:
                plane_utils.edge.level(self.__context, edges, max_z - z, False, self.__context.mat_wall_index)

        # Level edges specific categories
        for group, edges in [
            (g, e) for g, e in self.__context.edges_by_group.items()
            if not g.category.outline and g.category.level and len(e) > 2
        ]:
            plane_utils.edge.level(self.__context, edges, group.category.level, group.category.ground,
                                   self.__context.mat_wall_index)

    def __update_mesh_end(self):
        bm = self.__context.bmesh
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.001)

    def __update_mesh_apply(self):
        self.__logger.debug('Update mesh apply...')
        utils.blender.mesh.update(self.__context.bmesh, self.__context.mesh)

    # Method - Tools
    def __get_or_create_material(self, mat_name: str) -> int:
        material = self.__context.mesh.materials.get(mat_name)
        if not material:
            material = bpy.data.materials.get(mat_name)
            self.__context.mesh.materials.append(material)
        return self.__context.mesh.materials.values().index(material)

    @staticmethod
    def __one_edge_above_the_other(edge1: bmesh.types.BMEdge, edge2: bmesh.types.BMEdge):
        return utils.blender.bmesh.vert.same_2d_position(edge1.verts[0], edge2.verts[0]) \
               and utils.blender.bmesh.vert.same_2d_position(edge1.verts[1], edge2.verts[1])
