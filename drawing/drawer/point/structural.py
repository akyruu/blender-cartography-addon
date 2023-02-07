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
    def __init__(self, template: CartographyTemplate, hidden=False):
        CartographyRoomDrawer.__init__(self, 'Coordinate statements', template)
        self.__hidden = hidden

    # Methods -----------------------------------------------------------------
    # Draw
    def draw(self, room: CartographyRoom, collection: bpy.types.Collection):
        for group in [g for g in room.groups.values() if g.category.type == CartographyCategoryType.STRUCTURAL]:
            group_collection = utils.blender.collection.create(group.name, collection)
            for point in group.points:
                self.__draw_point(point, group_collection)

        # Hide collection if necessary
        utils.blender.collection.view_hide(collection, self.__hidden)

    def __draw_point(self, point: CartographyPoint, collection: bpy.types.Collection):
        template_item = self._get_template_category_item(self.__mappings.get(point.category) or point.category)
        if not template_item or not template_item.object:
            return

        obj = utils.blender.object.create_from_template(
            point.get_label(),
            point.location,
            template_item.object,
            collection
        )
        obj.hide_set(point.copy)
