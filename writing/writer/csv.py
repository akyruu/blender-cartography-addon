"""
Module for CSV writer
"""

import logging
from pathlib import Path
from typing import Optional, TextIO

import utils
from reading import CartographyFile, CartographyFileInfo, CartographyFilePoint, CartographyFileSide
from .common import CartographyWriter
from .. import utils as write_utils


# CLASSES =====================================================================
class CartographyCsvWriter(CartographyWriter):
    """CSV cartography writer"""

    # Fields ------------------------------------------------------------------
    __logger: logging.Logger = logging.getLogger('CartographyCsvWriter')

    # Constructor -------------------------------------------------------------
    def __init__(self, separator: str, logger: Optional[logging.Logger] = None):
        self.__separator = separator
        self.__logger = logger or self.__logger

    # Methods -----------------------------------------------------------------
    def write(self, file: CartographyFile, filepath: Optional[Path] = None):
        with open(filepath or file.path, 'w', encoding='utf8') as output:
            self.__write_headers(file, output)
            self.__write_points(file, output)

    # Header
    def __write_headers(self, file: CartographyFile, output: TextIO):
        for header in file.headers:
            if isinstance(header, CartographyFileInfo):
                self.__write_header_info(header, output)
            else:
                write_utils.line.write_obj(header, output)

    # FIXME used ?
    def __write_header_info(self, info: CartographyFileInfo, output: TextIO):
        write_utils.line.write(self.__separator, [
            'distance 1-2',  # Distance S1-S2 label
            str(info.s1s2_distance),  # Distance between S1 and S2
            ', '.join(info.scribes1),  # Scribe 2
            ', '.join(info.scribes2), '',  # Scribe 1
            ', '.join(info.explorers), '', '',  # Explorer
            'méthode des cercles'  # Coordinates label
        ], output)

    # Point
    def __write_points(self, file: CartographyFile, output: TextIO):
        for point in file.points:
            self.__write_point(point, output)

    def __write_point(self, point: CartographyFilePoint, output: TextIO):
        if point.side == CartographyFileSide.LEFT:
            side = 'G'
        elif point.side == CartographyFileSide.RIGHT:
            side = 'D'
        else:
            side = ''

        # FIXME use patterns config
        write_utils.line.write(self.__separator, [
            point.point_name,  # Point name
            side,  # Side
            utils.string.to_string(point.s1_distance),  # Distance to S1
            utils.string.to_string(point.s2_distance),  # Distance to S2
            utils.string.to_string(point.height),  # Height
            utils.string.to_string(point.category),  # Category
            utils.string.to_string(point.group_identifier),  # Group identifier
            utils.string.to_string(point.interest_type),  # Interest type
            utils.string.to_string(point.observations), '', '',  # Observations
            utils.string.to_string(point.location.y), '',  # Y
            utils.string.to_string(point.location.x), '',  # X
            utils.string.to_string(point.location.z)  # Z
        ], output)
