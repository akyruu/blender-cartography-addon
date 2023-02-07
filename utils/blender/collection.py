"""
Module for utility blender collection methods
"""

import logging

import bpy

# VARIABLES ===================================================================
__logger = logging.Logger('blender_collection')


# METHODS =====================================================================
def find(name: str, parent: bpy.types.Collection = None) -> bpy.types.Collection:
    collections = parent.children if parent else bpy.data.collections
    collection = collections.get(name, None)
    if not collection:
        for child in collections:
            collection = find(name, child)
            if collection:
                break
    return collection


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


def global_hide(collection: bpy.types.Collection, hidden: bool):
    collection.hide_viewport = hidden


def view_hide(collection: bpy.types.Collection, hidden: bool):
    view_layer = bpy.context.scene.view_layers['ViewLayer']
    view_collection = find(collection.name, view_layer.layer_collection)
    if not collection:
        __logger.warning('Collection %s not found in view layer', collection.name)
        return
    view_collection.hide_viewport = hidden
