"""
Module for utility blender collection methods
"""

import logging

import bpy

# VARIABLES ===================================================================
__logger = logging.Logger('blender_collection')


# METHODS =====================================================================
def get_or_create(name: str, parent: bpy.types.Collection = None) -> bpy.types.Collection:
    collection = bpy.data.collections.get(name)
    if not collection:
        collection = create(name, parent)
    return collection


def create(name: str, parent: bpy.types.Collection = None, erase=False) -> bpy.types.Collection:
    collection = bpy.data.collections.get(name)
    if collection:
        if not erase:
            return collection  # TODO add check parent

        __logger.debug('Collection <%s> already exists: delete previous instance', name)
        remove(collection)

    __logger.debug('Create a new collection: <%s>', name)
    collection = bpy.data.collections.new(name)
    (parent or bpy.context.scene.collection).children.link(collection)
    return collection


def remove(collection: bpy.types.Collection):
    # FIXME remove objects in collection not working (remove template object too)
    # objects = [object for object in collection.objects \
    #         if object.users == 1 and object not in self.__template.objects]
    # while objects:
    #     bpy.data.objects.remove(objects.pop())
    bpy.data.collections.remove(collection)
