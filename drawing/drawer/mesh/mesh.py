"""
Module for mesh drawer
"""

import logging

import bmesh
import bpy
from bmesh.types import BMesh
from bpy.types import Mesh
from mathutils import Vector

import utils
from model import CartographyCategoryType, CartographyObjectType, CartographyRoom
from templating import CartographyTemplate
from .group import CartographyMeshGroupContext, CartographyMeshGroupGeometry, CartographyMeshOutlineGroupDrawer, \
    CartographyMeshExtrudedGroupDrawer, CartographyMeshLeveledGroupDrawer
from ..common import CartographyRoomDrawer


# Classes =====================================================================
class CartographyMeshDrawer(CartographyRoomDrawer):
    """Drawer of mesh represents the room for cartography"""

    # Fields ------------------------------------------------------------------
    __logger = logging.getLogger('CartographyPointDrawer')

    # Constructor -------------------------------------------------------------
    def __init__(self, template: CartographyTemplate):
        CartographyRoomDrawer.__init__(self, 'mesh', template)
        self.__outline_drawer = CartographyMeshOutlineGroupDrawer()
        self.__drawers = {
            lambda c: c.options.outline: self.__outline_drawer,
            lambda c: c.options.level: CartographyMeshExtrudedGroupDrawer(),
            lambda c: c.options.ground: CartographyMeshLeveledGroupDrawer()
        }

    # Methods -----------------------------------------------------------------
    def draw(self, room: CartographyRoom, collection: bpy.types.Collection):
        # Get template
        template = self._get_template_object(CartographyObjectType.PLANE, 'object type')
        if template is None:
            return

        # Create object
        name = room.name + '_plane'
        obj = utils.blender.object.create(name, Vector((0, 0, 0)), template, collection)

        # Create and clean BMesh
        mesh = utils.blender.object.get_mesh(obj)
        bm = utils.blender.mesh.edit(mesh)
        utils.blender.bmesh.ops.clean(bm)

        # Draw room
        self.__draw_room(mesh, bm, room)

        # Clean BMesh and update mesh
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.001)
        utils.blender.mesh.update(mesh, bm)

    def __draw_room(self, mesh: Mesh, bm: BMesh, room: CartographyRoom):
        context = CartographyMeshGroupContext(mesh, bm, room)

        self.__logger.debug('Draw mesh for room <%s>...', room.name)
        groups = [g for g in room.groups.values() if g.category.type == CartographyCategoryType.STRUCTURAL]
        groups = sorted(groups, key=lambda g: g.category.value)
        for group in groups:
            context.group = group
            geom = self.__draw_group(context)

            if group.category.options.outline:
                context.outline_geom = geom
            else:
                context.geom_by_group[group.name] = geom

        # Draw room ground at the end because the others forms is required
        self.__logger.debug('Draw ground for room <%s>...', room.name)
        context.group = room.outline_group
        self.__outline_drawer.draw_ground_face(context)

    def __draw_group(self, context: CartographyMeshGroupContext) -> CartographyMeshGroupGeometry:
        group = context.group
        drawer = utils.collection.list.inext(d for p, d in self.__drawers.items() if p(group.category))
        if drawer:
            try:
                geom = drawer.draw(context)
                self.__check_group_geom(geom)
            except Exception as err:
                raise Exception('Failed to draw group <{}>'.format(group.name)).with_traceback(err.__traceback__)
        else:
            self.__logger.warning('No drawer found for group <%s> (%s)', group.name, group.category.name)
            geom = CartographyMeshGroupGeometry()

        return geom

    @staticmethod
    def __check_group_geom(geom: CartographyMeshGroupGeometry):
        for vert in geom.vertices:
            duplicated = [v for v in geom.vertices if utils.blender.bmesh.vert.same_3d_position(v, vert)]
            count = len(duplicated)
            if count > 1:
                raise Exception('Duplicated vertex <{}>: <{}> times'.format(vert.co, count))

        edges_dict = {'': geom.edges, 'based': geom.based_edges}
        for name, edges in edges_dict.items():
            for edge in edges:
                duplicated = [e for e in edges if utils.blender.bmesh.edge.same_3d_position(e, edge)]
                count = len(duplicated)
                if count > 1:
                    raise Exception('Duplicated {} edge <{}>: <{}> times'.format(name, [v.co for v in edge.verts], count))

        # TODO check faces ?
