import logging
import os

import utils
from drawing import CartographyDrawer, CartographyInterestPointDrawer, CartographyMeshDrawer, \
    CartographyStructuralPointDrawer
from drawing.template.reader import CartographyTemplateReader
from parsing import CartographyParser
from reading import CartographyCsvReader, CartographyTsvReader
from reading.config.table import ModelVersion

# VARIABLES ===================================================================
name = 'generate_blender_file'
__logger = logging.getLogger(name)


# METHODS =====================================================================
def entry_point(args: any):
    utils.blender.scene.clear()
    file = args.file
    if not file:
        raise Exception(f'A file required for action <{name}>')
    execute(file)
    if args.output:
        utils.blender.io.export_blend_file(args.output)


def execute(filepath: os.path):
    """Read, parse a CSV file and create the room from coordinates"""
    __logger.info('Generation of blender file start...')
    file = __read_csv_file(filepath, ModelVersion.v1_3)
    room = __parse_cartography_file(file)
    template = __read_blender_template()
    __draw_blender_model(room, template)
    __logger.info('Generation of blender file finished with success!')


def __read_csv_file(filepath, version: ModelVersion):
    __logger.info('Read CSV file <%s>', filepath)
    filename, extension = os.path.splitext(filepath)
    if extension.lower() == '.tsv':
        reader = CartographyTsvReader(version, True)
    else:  # if extension is '.csv':
        separator = '\t'  # TODO open popup for ask to user choose the file separator
        reader = CartographyCsvReader(separator, version, True)
    file = reader.read(filepath)
    __logger.info('CSV file <%s> read with success! %d points found', filepath, len(file.points))
    return file


def __parse_cartography_file(file):
    __logger.info('Parse CSV file <%s>', file.path)
    parser = CartographyParser()
    room = parser.parse(file)
    __logger.info('CSV file <%s> parsed with success! %d points found!', file.path, len(file.points))
    return room


def __read_blender_template():
    blend_path = os.path.join(utils.io.path.workspace(), 'bca-template.blend')
    __logger.info('Read .blend utils <%s>', blend_path)
    reader = CartographyTemplateReader()
    template = reader.read(blend_path)
    __logger.info('Template .blend <%s> read with success!', blend_path)
    return template


def __draw_blender_model(room, template):
    __logger.info('Draw room <%s>', room.name)
    drawer = CartographyDrawer(
        template,
        CartographyStructuralPointDrawer(template, hidden=True),
        CartographyMeshDrawer(template),
        CartographyInterestPointDrawer(template)
    )
    drawer.draw(room)
    __logger.info('<%s> room drawn with success!', room.name)
