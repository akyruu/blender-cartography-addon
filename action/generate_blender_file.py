import logging
import os

import utils
from drawing import CartographyDrawer, CartographyInterestPointDrawer, CartographyStructuralPointDrawer, \
    CartographyPlaneDrawer, CartographyMeshDrawer
from parsing import CartographyParser
from reading import CartographyCsvReader, CartographyTsvReader
from templating import CartographyTemplateReader

# VARIABLES ===================================================================
name = 'generate_blender_file'
__logger = logging.getLogger(name)


# METHODS =====================================================================
def entry_point(args: any):
    utils.blender.scene.clear()
    file = args.file
    if not file:
        raise Exception('A file required for action <{}>'.format(name))
    execute(file)
    if args.output:
        utils.blender.io.export_blend_file(args.output)


def execute(filepath: os.path):
    """Read, parse a CSV file and create the room from coordinates"""
    __logger.info('Generation of blender file start...')
    file = __read_csv_file(filepath)
    room = __parse_cartography_file(file)
    template = __read_blender_template()
    __draw_blender_model(room, template)
    __logger.info('Generation of blender file finished with success!')


def __read_csv_file(filepath):
    __logger.info('Read CSV file <%s>', filepath)
    filename, extension = os.path.splitext(filepath)
    if extension.lower() == '.tsv':
        reader = CartographyTsvReader()
    else:  # if extension is '.csv':
        separator = '\t'  # TODO open popup for ask to user choose the file separator
        reader = CartographyCsvReader(separator)
    file = reader.read(filepath)
    __logger.info('CSV file <%s> read with success!', filepath)
    return file


def __parse_cartography_file(file):
    __logger.info('Parse CSV file <%s>', file.path)
    parser = CartographyParser()
    room = parser.parse(file)
    __logger.info('CSV file <%s> parsed with success!', file.path)
    return room


def __read_blender_template():
    blend_path = os.path.join(utils.io.path.workspace(), 'bca-template.blend')
    __logger.info('Read .blend template <%s>', blend_path)
    reader = CartographyTemplateReader()
    template = reader.read(blend_path)
    __logger.info('Template .blend <%s> read with success!', blend_path)
    return template


def __draw_blender_model(room, template):
    __logger.info('Draw room <%s>', room.name)
    drawer = CartographyDrawer(
        template,
        # CartographyInterestPointDrawer(template),
        CartographyStructuralPointDrawer(template),
        # CartographyPlaneDrawer(template)
        CartographyMeshDrawer(template)
    )
    drawer.draw(room)
    __logger.info('<%s> room drawn with success!', room.name)
