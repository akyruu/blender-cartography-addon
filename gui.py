"""
Module for GUI

History:
2020/08/21: v0.0.1
    + add CSV/TSV import action
    + add CSV/TSV import operator
    + add menu item in File > Import
2020/09/01: v0.0.2
    + update relating to reader/parser separation
"""
import logging
import sys

import bpy
import bpy_extras

import bca_main


# Classes =====================================================================
# Actions ---------------------------------------------------------------------
class CartographyCsvImportAction:
    __logger = logging.getLogger('CartographyCsvImportAction')

    def __init__(self, filepath):
        self.filepath = filepath

    def execute(self):
        bca_main.read_csv_file(self.filepath)


# Actions ---------------------------------------------------------------------
class CartographyCsvImportOperator(bpy.types.Operator, bpy_extras.io_utils.ImportHelper):
    bl_idname = 'scene.cartography_csv_import_operator'
    bl_label = 'Cartography (.csv, .tsv)'
    bl_description = 'Import cartography from CSV file'

    filter_glob: bpy.props.StringProperty(
        default='*.csv,*.tsv',
        options={'HIDDEN'},
    )

    def execute(self, context):
        CartographyCsvImportAction(self.filepath).execute()  # noqa
        return {'FINISHED'}


# Menu ------------------------------------------------------------------------
def draw_menu(self):
    self.layout.operator(CartographyCsvImportOperator.bl_idname, text='Cartography (.csv, .tsv)')


# [UN]REGISTER ================================================================
__classes__ = (
    # CartographyCsvImportAction,
    # CartographyCsvImportOperator,
)


def register():
    if 'DEBUG_MODE' not in sys.argv:
        bpy.types.TOPBAR_MT_file_import.append(draw_menu)


def unregister():
    if 'DEBUG_MODE' not in sys.argv:
        bpy.types.TOPBAR_MT_file_import.remove(draw_menu)
