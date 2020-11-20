"""
Module for utility blender I/O methods
"""

import os

import bpy


# METHODS =====================================================================
def export_blend_file(filepath: os.path):
    if os.path.exists(filepath):
        os.remove(filepath)
    bpy.ops.wm.save_as_mainfile(filepath=filepath)
