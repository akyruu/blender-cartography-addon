"""
Module for interest point drawer
"""

import logging

import bpy
from mathutils import Vector

import utils
from model import CartographyPoint, CartographyCategory, CartographyCategoryType, CartographyInterestType, \
    CartographyRoom
from ..common import CartographyRoomDrawer, CartographyTemplate


# Classes =====================================================================
class CartographyInterestPointDrawer(CartographyRoomDrawer):
    """Drawer of interest points in room for cartography"""

    # Fields ------------------------------------------------------------------
    __logger = logging.getLogger('CartographyInterestPointDrawer')

    # Constructor -------------------------------------------------------------
    def __init__(self, template: CartographyTemplate):
        CartographyRoomDrawer.__init__(self, 'Interest Points', template)

    # Methods -----------------------------------------------------------------
    # Draw
    def draw(self, room: CartographyRoom, collection: bpy.types.Collection):
        for point in [p for p in room.all_points if p.category.type == CartographyCategoryType.INTEREST]:
            if point.category == CartographyCategory.ANTHROPOGENIC_OBJECT:
                point_collection = utils.blender.collection.create('Objects', collection)
                drawn = self.__draw_anthropogenic_object(point, point_collection)
            else:
                point_collection = utils.blender.collection.create('Others', collection)
                drawn = self.__draw_other(point, point_collection)

            if not drawn:
                self.__draw_unknown(point, point_collection)

    def __draw_anthropogenic_object(self, point: CartographyPoint, collection: bpy.types.Collection) -> bool:
        self.__logger.debug('Draw anthropogenic object: <%s>', str(point))

        # Check point
        if point.interest is None:  # FIXME move the unknown code ?
            self.__logger.warning('An interest is required for anthropic object point: <%s>.', str(point))
            return False
        else:
            interest = point.interest[0]  # TODO treat multiple interests
            template = self._get_template_object(interest, 'interest type')

        # Get template
        if template is None:
            self.__logger.error('No template found for anthropogenic object: <%s>. Ignored', point.interest[0])
            return False

        # Create objects
        z = point.location.z
        for i in range(point.interest[1]):
            location = Vector((point.location.x, point.location.y, z))
            obj = utils.blender.object.create(point.get_label(), location, template, collection)

            z += obj.dimensions.z  # noqa
        return True

    def __draw_other(self, point: CartographyPoint, collection: bpy.types.Collection) -> bool:
        self.__logger.debug('Draw interest point: <%s>', str(point))

        # Get template and create point
        template = self._get_template_object(point.category, 'category')
        if template is None:
            self.__logger.warning('No template found for interest point: <%s>.', str(point))
            return False
        obj = utils.blender.object.create(point.get_label(), point.location, template, collection)

        # Icon
        if point.interest is not None:
            interest = point.interest[0]  # TODO treat multiple interests

            # Get icon template
            template = self._get_template_object(interest, 'interest type')
            if template is None:
                self.__logger.warning('No template found for interest type: <%s>.', str(interest))
                return False

            # Create image
            name = obj.name + '_icon'
            z = obj.location.z + obj.dimensions.z  # noqa
            utils.blender.object.create(name, (obj.location[0], obj.location[1], z), template, collection)
        return True

    def __draw_unknown(self, point: CartographyPoint, collection: bpy.types.Collection):
        self.__logger.debug('Draw unknown point', point, collection)

        # FIXME determined model with icon with config ?
        base_template = self._get_template_object(CartographyCategory.UNKNOWN, 'category')
        base_obj_name = point.name + ' (' + ', '.join(point.observations) + ')'
        obj = utils.blender.object.create(base_obj_name, point.location, base_template, collection)

        # Create image
        icon_template = self._get_template_object(CartographyInterestType.UNKNOWN, 'interest type')
        icon_obj_name = base_obj_name + '_icon'
        z = obj.location.z + obj.dimensions.z  # noqa
        utils.blender.object.create(icon_obj_name, (obj.location[0], obj.location[1], z), icon_template, collection)
