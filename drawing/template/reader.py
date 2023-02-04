"""
Module for template reader
"""

import logging
import os

import bpy
from drawing import config as draw_config
from .model import CartographyTemplate


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
        for obj_type, obj_name in draw_config.template.by_object.items():
            template.objects[obj_type] = self.__find_object_by_name(obj_name) if obj_name is not None else None
        return template

    @staticmethod
    def __filter_already_exists(source, target):
        return [item for item in source if item not in target]

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
