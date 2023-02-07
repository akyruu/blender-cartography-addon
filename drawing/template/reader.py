"""
Module for utils reader
"""

import logging
import os
from enum import Enum
from typing import Dict

import bpy
from .model import CartographyTemplate, CartographyTemplateItem
from .. import config as draw_config
from ..config.model import CartographyTemplateConfig


# Classes =====================================================================
class CartographyTemplateReader:
    """Template writer (.blend) for cartography"""

    # Fields ------------------------------------------------------------------
    __logger = logging.getLogger('CartographyTemplateReader')

    # Methods -----------------------------------------------------------------
    def read(self, filepath: os.path) -> CartographyTemplate:
        with bpy.data.libraries.load(filepath) as (data_from, data_to):
            data_to.objects = self.__filter_already_exists(data_from.objects, bpy.data.objects)  # import materials too

        template = CartographyTemplate(filepath)
        template.item_by_category = self.__build_item_by_enum(draw_config.template.by_category)
        template.item_by_interest_type = self.__build_item_by_enum(draw_config.template.by_interest_type)
        template.item_by_object_type = self.__build_item_by_enum(draw_config.template.by_object_type)

        return template

    @staticmethod
    def __filter_already_exists(source, target):
        return [item for item in source if item not in target]

    @staticmethod
    def __build_item_by_enum(template_config: CartographyTemplateConfig) -> Dict[Enum, CartographyTemplateItem]:
        item_by_enum = {}
        for enum, item_config in template_config.items_by_enum.items():
            item_object = CartographyTemplateReader.__find_object_by_name(item_config.name)
            item_by_enum[enum] = CartographyTemplateItem(item_config, item_object)
        return item_by_enum

    @staticmethod
    def __find_object_by_name(name: str) -> bpy.types.Object:
        obj = next((obj for obj in bpy.data.objects if obj.name == name), None)
        if obj is None:
            CartographyTemplateReader.__logger.warning('Object not found: %s', name)
        return obj


# [UN]REGISTER ================================================================
__classes__ = (
    # CartographyTemplate
    # CartographyTemplateReader
)
