"""
Module for drawing

History:
2020/08/21: v0.0.1
    + add cartography drawing
    + add cartography room drawing (point + plane)
"""

import logging

import utils
from model import CartographyRoom
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
    def draw(self, room: CartographyRoom):
        parent = utils.blender.collection.create(room.name)
        for roomDrawer in self.__room_drawers:
            collection = utils.blender.collection.create(roomDrawer.name, parent)
            roomDrawer.draw(room, collection)
