"""
Module for utility blender scene methods
"""

import bpy


# METHODS =====================================================================
def clear():
    bpy.ops.object.delete({'selected_objects': [bpy.context.scene.objects['Cube']]})
