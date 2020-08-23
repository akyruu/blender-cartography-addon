"""
Module for GUI

History:
2020/08/21: v0.0.1
    + add CSV/TSV import action
    + add CSV/TSV import operator
    + add menu item in File > Import
"""

import logging
import os
import sys

import bpy
import bpy_extras

import bca_utils
from drawing import CartographyDrawer, CartographyInterestPointDrawer, CartographyStructuralPointDrawer, \
    CartographyPlaneDrawer
from reading import CartographyReader
from templating import CartographyTemplateReader


# __classes__ =====================================================================
# Actions ---------------------------------------------------------------------
class CartographyCsvImportAction:
    __logger = logging.getLogger('CartographyCsvImportAction')

    def __init__(self, filepath):
        self.filepath = filepath

    def execute(self):
        # Read CSV file
        self.__logger.info('Read CSV file <%s>', self.filepath)
        reader = CartographyReader(self.filepath)
        rooms = reader.read()
        self.__logger.info('CSV file <%s> read with success!', self.filepath)

        # Read .blend template
        blend_path = os.path.join(bca_utils.path_workspace(), 'bca-template.blend')
        self.__logger.info('Read .blend template <%s>', blend_path)
        reader = CartographyTemplateReader()
        template = reader.read(blend_path)
        self.__logger.info('Template .blend <%s> read with success!', blend_path)

        # Draw cartography
        self.__logger.info('Draw <%d> room(s)', len(rooms))
        drawer = CartographyDrawer(
            template,
            CartographyInterestPointDrawer(template),
            CartographyStructuralPointDrawer(template),
            CartographyPlaneDrawer(template)
        )
        drawer.draw(rooms.values())
        self.__logger.info('<%d> room(s) drawn with success!', len(rooms))

        self.__logger.info('Import finished with success!')


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


# FIXME move this method in greater location
def debug():
    CartographyCsvImportAction(os.path.join(bca_utils.path_workspace(), 'samples/coordinates_01.tsv')).execute()
