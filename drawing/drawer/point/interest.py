"""
Module for interest point drawer
"""

import logging

import bpy
from mathutils import Vector

import utils
from model import CartographyPoint, CartographyCategory, \
    CartographyCategoryType, CartographyRoom
from ..common import CartographyRoomDrawer


# Classes =====================================================================
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
            obj = utils.blender.object.create(point.name, Vector((point.location.x, point.location.y, z)), template,
                                              collection)
            z += obj.dimensions.z  # noqa
        return

    def __draw_other(self, point: CartographyPoint, collection: bpy.types.Collection):
        # Get template and create point
        template = self._get_template_object(point.category, 'category')
        if template is None:
            return
        obj = utils.blender.object.create(point.name, point.location, template, collection)

        # Icon
        if point.interest is not None:
            # Get icon template
            template = self._get_template_object(point.interest[0], 'interest type')
            if template is None:
                return

            # Create image
            name = obj.name + '_icon'
            z = obj.location.z + obj.dimensions.z  # noqa
            utils.blender.object.create(name, Vector((obj.location.x, obj.location.y, z)), template, collection)  # noqa
