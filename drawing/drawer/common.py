"""
Module for room drawer
"""

import logging
from abc import abstractmethod
from enum import Enum

import bpy

from model import CartographyRoom
from templating import CartographyTemplate


# Classes =====================================================================
class CartographyRoomDrawer:
    """Abstract drawer of room for cartography"""

    # Fields ------------------------------------------------------------------
    __logger = logging.getLogger('CartographyRoomDrawer')

    # Constructor -------------------------------------------------------------
    def __init__(self, name: str, template: CartographyTemplate):
        self.name = name
        self._template = template

    # Methods -----------------------------------------------------------------
    # Draw
    @abstractmethod
    def draw(self, room: CartographyRoom, collection: bpy.types.Collection):
        pass

    # Tools
    def _get_template_object(self, enum: Enum, enum_type: str) -> bpy.types.Object:
        template = self._template.objects.get(enum, None)
        if template is None:
            self.__logger.warning('Template not found for %s <%s>', enum_type, enum.name)
        return template
