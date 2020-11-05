import argparse
import logging
import os
import bpy
import io

import bca_utils
from drawing import CartographyDrawer, CartographyInterestPointDrawer, CartographyStructuralPointDrawer, \
    CartographyPlaneDrawer
from parsing import CartographyParser
from reading import CartographyCsvReader, CartographyTsvReader
from templating import CartographyTemplateReader

# VARIABLES ===================================================================
__logger = logging.getLogger('main')

# ARGUMENTS ===================================================================
arg_parser = argparse.ArgumentParser()
arg_parser.add_argument(
    '-a', '--action',
    type=str,
    help='Launch a main action directly'
)
arg_parser.add_argument(
    '-e', '--export',
    type=str,
    help='Blend file to export created room'
)
arg_parser.add_argument(
    '-f', '--file',
    type=str,
    help='File with coordinates, required for certain actions'
)
args, unknown = arg_parser.parse_known_args()


# METHODS =====================================================================
def entry_point(action: str):
    """Entry point for execute an action"""
    __logger.info('Launch action <{}>...', action)
    if action == 'read_csv_file':
        clear_scene()
        file = args.file
        if not file:
            raise Exception('A file required for action <{}>'.format(action))
        read_csv_file(file)
        if args.export:
            export(args.export)
    else:
        raise Exception('Unknown action: <{}>'.format(action))


def clear_scene():
    bpy.ops.object.delete({'selected_objects': [bpy.context.scene.objects['Cube']]})


def read_csv_file(filepath: os.path):
    """Read, parse a CSV file and create the room from coordinates"""
    # Read CSV file
    __logger.info('Read CSV file <%s>', filepath)
    filename, extension = os.path.splitext(filepath)
    if extension.lower() == '.tsv':
        reader = CartographyTsvReader()
    else:  # if extension is '.csv':
        separator = '\t'  # TODO open popup for ask to user choose the file separator
        reader = CartographyCsvReader(separator)
    file = reader.read(filepath)
    __logger.info('CSV file <%s> read with success!', filepath)

    # Parse CSV file
    __logger.info('Parse CSV file <%s>', filepath)
    parser = CartographyParser()
    room = parser.parse(file)
    __logger.info('CSV file <%s> parsed with success!', filepath)

    # Read .blend template
    blend_path = os.path.join(bca_utils.path_workspace(), 'bca-template.blend')
    __logger.info('Read .blend template <%s>', blend_path)
    reader = CartographyTemplateReader()
    template = reader.read(blend_path)
    __logger.info('Template .blend <%s> read with success!', blend_path)

    # Draw cartography
    __logger.info('Draw room <%s>', room.name)
    drawer = CartographyDrawer(
        template,
        CartographyInterestPointDrawer(template),
        CartographyStructuralPointDrawer(template),
        CartographyPlaneDrawer(template)
    )
    drawer.draw(room)
    __logger.info('<%s> room drawn with success!', room)

    __logger.info('Import finished with success!')


def export(filepath: os.path):
    if os.path.exists(filepath):
        os.remove(filepath)
    bpy.ops.wm.save_as_mainfile(filepath=filepath)
