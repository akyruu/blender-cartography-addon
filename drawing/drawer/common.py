"""
Module for room drawer
"""

import logging
from abc import abstractmethod

import bpy
from model import CartographyRoom, CartographyCategory, CartographyInterestType, CartographyObjectType
from ..template.model import CartographyTemplate, CartographyTemplateItem


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
    def _get_template_category_item(self, category: CartographyCategory) -> CartographyTemplateItem:
        template_item = self._template.get_category_item(category)
        if template_item is None:
            self.__logger.warning('Template not found for %s <%s>', 'category', category.name)
        return template_item

    def _get_template_interest_item(self, interest_type: CartographyInterestType) -> CartographyTemplateItem:
        template_item = self._template.get_interest_item(interest_type)
        if template_item is None:
            self.__logger.warning('Template not found for %s <%s>', 'interest type', interest_type.name)
        return template_item

    def _get_template_object_item(self, object_type: CartographyObjectType) -> CartographyTemplateItem:
        template_item = self._template.get_object_item(object_type)
        if template_item is None:
            self.__logger.warning('Template not found for %s <%s>', 'object type', object_type.name)
            return None
        return template_item
