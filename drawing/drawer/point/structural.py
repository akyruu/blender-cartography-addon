"""
Module for structural point drawer
"""

import logging

import bpy

import utils
from drawing.drawer.common import CartographyRoomDrawer, CartographyTemplate
from model import CartographyPoint, CartographyCategory, \
    CartographyCategoryType, CartographyRoom


# Classes =====================================================================
class CartographyStructuralPointDrawer(CartographyRoomDrawer):
    """Drawer of structural points in room for cartography"""

    # Fields ------------------------------------------------------------------
    __logger = logging.getLogger('CartographyStructuralPointDrawer')
    __mappings = {
        CartographyCategory.BASEMENT: CartographyCategory.ESCARPMENT,
        CartographyCategory.LANDING: CartographyCategory.ESCARPMENT,
        CartographyCategory.COLUMN_BASE: CartographyCategory.COLUMN
    }

    # Constructor -------------------------------------------------------------
    def __init__(self, template: CartographyTemplate):
        CartographyRoomDrawer.__init__(self, '', template)

    # Methods -----------------------------------------------------------------
    # Draw
    def draw(self, room: CartographyRoom, collection: bpy.types.Collection):
        for group in [g for g in room.groups.values() if g.category.type == CartographyCategoryType.STRUCTURAL]:
            group_collection = utils.blender.collection.create(group.name, collection)
            for point in group.points:
                self.__draw_point(point, group_collection)

    def __draw_point(self, point: CartographyPoint, collection):
        template = self._get_template_object(self.__mappings.get(point.category) or point.category, 'category')
        if template is None:
            return

        obj = utils.blender.object.create(point.get_label(), point.location, template, collection)
        obj.hide_set(point.copy)
