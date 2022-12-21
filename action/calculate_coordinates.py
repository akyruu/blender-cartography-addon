import logging
import os
import shutil
from pathlib import Path

import config.patterns
import utils
from config.patterns import ColumnModelCategory
from mathutils import Vector
from reading import CartographyCsvReader, CartographyFile, CartographyFileSide, CartographyTsvReader
from writing import CartographyCsvWriter, CartographyTsvWriter

# VARIABLES ===================================================================
name = 'calculate_coordinates'
__logger = logging.getLogger(name)


# METHODS =====================================================================
def entry_point(args: any):
    file = args.file
    if not file:
        raise Exception('A file required for action <{}>'.format(name))

    target_path = args.output if args.output else file
    execute(file, target_path)


def execute(filepath: os.path, target_path: os.path):
    """Read a CSV file, calculate coordinates and update the CSV file"""
    __logger.info('Calculation of coordinates start...')
    file = __read_csv_file(filepath)
    __calculate_coordinates(file)
    if not target_path or target_path == filepath:
        __backup_csv_file(file)
        __write_csv_file(file, filepath)
    else:
        __write_csv_file(file, target_path)
    __logger.info('Calculation of coordinates finished with success!')


def __read_csv_file(filepath: os.path) -> CartographyFile:
    __logger.info('Read CSV file <%s>', filepath)

    filename, extension = os.path.splitext(filepath)
    if extension.lower() == '.tsv':
        reader = CartographyTsvReader(config.patterns.excel.exclude(ColumnModelCategory.COORDINATE))
    else:  # if extension is '.csv':
        separator = '\t'  # TODO open popup for ask to user choose the file separator
        reader = CartographyCsvReader(separator, config.patterns.excel.exclude(ColumnModelCategory.COORDINATE))
    file = reader.read(filepath)

    __logger.info('CSV file <%s> read with success! %d points found', filepath, len(file.points))
    return file


def __calculate_coordinates(file: CartographyFile):
    for point in file.points:
        point.location = utils.math.calc_coordinates_by_dist(
            Vector((point.s1_distance, point.s2_distance, point.height)),
            file.info.s1s2_distance,
            point.side == CartographyFileSide.LEFT
        )


def __backup_csv_file(file: CartographyFile):
    __logger.info('Create backup of CSV file <%s>', file.path)

    i = 0
    backup_path = Path(file.path + '.bak')
    while backup_path.exists():
        backup_path = Path(file.path + '.' + str(i) + '.bak')
        i += 1
    shutil.copyfile(file.path, backup_path)

    __logger.info('Backup of CSV file <%s> (<%s>) created with success!', file.path, backup_path)


def __write_csv_file(file: CartographyFile, target_path: os.path):
    __logger.info('Write CSV file <%s>', target_path)

    filename, extension = os.path.splitext(target_path)
    if extension.lower() == '.tsv':
        writer = CartographyTsvWriter()
    else:  # if extension is '.csv':
        separator = '\t'  # TODO open popup for ask to user choose the file separator
        writer = CartographyCsvWriter(separator)
    writer.write(file, target_path)

    __logger.info('CSV file <%s> write with success!', target_path)
    return file
