"""
Module for utils model
"""

import os
from typing import Dict, NamedTuple

import bpy
from model import CartographyCategory, CartographyInterestType, CartographyObjectType
from ..config.model import CartographyTemplateConfigItem


# Classes =====================================================================

class CartographyTemplateItem(NamedTuple):
    """Template's item for cartography"""
    config: CartographyTemplateConfigItem
    object: bpy.types.Object


class CartographyTemplate:
    """Template for cartography"""

    # Constructor -------------------------------------------------------------
    def __init__(self, filepath: os.path):
        self.filepath = filepath
        self.item_by_category: Dict[CartographyCategory, CartographyTemplateItem] = {}
        self.item_by_interest_type: Dict[CartographyInterestType, CartographyTemplateItem] = {}
        self.item_by_object_type: Dict[CartographyObjectType, CartographyTemplateItem] = {}

    def get_category_item(self, category: CartographyCategory) -> bpy.types.Object:
        return self.item_by_category.get(category, None)

    def get_interest_item(self, interest_type: CartographyInterestType) -> bpy.types.Object:
        return self.item_by_interest_type.get(interest_type, None)

    def get_object_item(self, object_type: CartographyObjectType) -> bpy.types.Object:
        return self.item_by_object_type.get(object_type, None)
