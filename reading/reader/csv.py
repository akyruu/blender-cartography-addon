"""
Module for CSV reader
"""

import logging
import os
from typing import Optional

from mathutils import Vector

import config
import utils
from .common import CartographyReader
from .. import utils as read_utils
from ..exception import CartographyReaderException
from ..model import CartographyFile, CartographyFileInfo, CartographyFileLine, CartographyFilePoint, \
    CartographyFileSide, ReadContext


# CLASSES =====================================================================
class CartographyCsvReader(CartographyReader):
    """CSV cartography reader"""

    # Fields ------------------------------------------------------------------
    __logger: logging.Logger = logging.getLogger('CartographyCsvReader')

    # Constructor -------------------------------------------------------------
    def __init__(self, separator: str, logger: Optional[logging.Logger] = None):
        self.__context = ReadContext(separator, logger or self.__logger)
        self.__file: Optional[CartographyFile] = None
        self.__header: bool = True
        self.__header_info: int = -1
        self.__last_point_side = None

    # Methods -----------------------------------------------------------------
    # Reading
    def read(self, filepath: os.path) -> CartographyFile:
        self.__file = CartographyFile(filepath)
        self.__header = True
        self.__header_info = -1
        self.__context.row = 0
        self.__context.column = 0

        with open(filepath, 'r', encoding='utf8') as file:
            # Read all lines in CSV file
            for line in file:
                self.__context.row += 1
                line = line.strip()
                if not line:
                    continue
                elif line.startswith('#'):
                    read_utils.line.ignore(self.__context, line)
                    continue
                elif self.__header:
                    read = False
                    if self.__header_info == 0:
                        read = self.__read_header_info(line)

                    if not read:
                        self.__read_header(line)
                else:
                    self.__read_point(line)

            # Check if a point found
            if self.__header:
                raise CartographyReaderException(
                    self.__context.row,
                    self.__context.column,
                    'Only header was found!',
                    'header',
                    'A line of type "point"'
                )

        return self.__file

    def __read_header(self, line: str):
        self.__file.headers.append(CartographyFileLine(self.__context.row, line))
        if self.__header_info < 0 and read_utils.line.check(self.__context, line, 'header', [
            'position, de 2', '', 'scribe 1', 'scribe 2', '', 'explorateur'
        ], False):
            self.__logger.debug('Header of information found!')
            self.__header_info = 0
        elif read_utils.line.check(self.__context, line, 'header', [
            'point :',
            '(côté|cote|side) : [GL]/[DR]',
            'Distance (à|to) S1',
            'Distance (à|to) S2',
            '(Hauteur|Height)',
            'Observations?', '', '',
            'Y', '',
            'X', '',
            'Z', '', '', '', '',
            'Adjacent \\(Y\\)'
        ], False):
            self.__logger.debug('Header of point table found!')
            self.__header = False

    def __read_header_info(self, line: str) -> bool:
        # Check line describe the info from header
        patterns = [
            'distance 1-2',  # Distance S1-S2 label
            '([0-9]+)',  # Distance between S1 and S2
            '(.+)',  # Scribe 1
            '(.+)', '',  # Scribe 2
            '(.+)', '', '',  # Explorer
            'méthode des cercles'  # Coordinates label
        ]
        matches = read_utils.line.check(self.__context, line, 'header', patterns, False)
        if not matches:
            return False

        self.__logger.debug('Header information line found: #%d', self.__context.row)
        info = CartographyFileInfo(self.__context.row, line)
        info.s1s2_distance = int(matches[1].group(0))
        info.scribes1 = matches[2].group(0).split(', ?')
        info.scribes2 = matches[3].group(0).split(', ?')
        info.explorers = matches[5].group(0).split(', ?')
        self.__file.info = info
        self.__file.headers.append(info)

        self.__header_info = 1
        return True

    def __read_point(self, line: str):
        # Check line describe a point
        patterns = [
            'point [0-9]+',  # Point name (0)
            '[DGRL]?',  # Side (1)
            '([0-9]+)?',  # Distance to S1 (2)
            '([0-9]+)?',  # Distance to S2 (3)
            '-?([0-9]+)?',  # Height (4)
            '([A-Za-z0-9].+)', '', '',  # Observations (5)
            '-?[0-9]+', '',  # Y (8)
            '-?[0-9]+', '',  # X (10)
            '-?[0-9]+', '', '', '', '',  # Z (12)
            '(.+)?'  # Adjacent Y (17)
        ]
        matches = read_utils.line.check(self.__context, line, 'point', patterns, False)
        if not matches:
            matches = read_utils.line.check(self.__context, line, 'point', ['point [0-9]+'], False, True)
            if not matches:
                raise CartographyReaderException(
                    self.__context.row,
                    self.__context.column,
                    line,
                    'point',
                    '|'.join(patterns)
                )
            read_utils.line.ignore(self.__context, line)
            return

        # Create a new point
        self.__logger.debug('Point line found: #%d', self.__context.row)
        point = CartographyFilePoint(self.__context.row, line)

        # Determine string information
        point.point_name = matches[0].group(0)
        point.s1_distance = int(matches[2].group(0)) if matches[2].group(0) else 0
        point.s2_distance = int(matches[3].group(0)) if matches[3].group(0) else 0
        point.height = int(matches[4].group(0)) if matches[4].group(0) else 0

        # Determine coordinates
        point.location = Vector((
            int(matches[8].group(0)),
            int(matches[10].group(0)),
            int(matches[12].group(0))
        ))

        # Determine point side
        side = matches[1].group(0)
        if not side:
            if not self.__last_point_side:
                self.__logger.warning('No point side found. The side is unknown')
                point.side = CartographyFileSide.UNKNOWN
            else:
                self.__logger.warning('No point side found. Use the last side used: <%s>', self.__last_point_side)
                point.side = self.__last_point_side
        elif utils.string.match_ignore_case('[GL]', side):
            point.side = CartographyFileSide.LEFT
        elif utils.string.match_ignore_case('[DR]', side):
            point.side = CartographyFileSide.RIGHT

        if not point.side:
            raise CartographyReaderException(self, side, 'point side', '[DGRL]')
        self.__last_point_side = point.side

        # Determine observations
        observations = matches[5].group(0)
        if observations:
            point.observations = [o.strip() for o in observations.split(config.obs_separator)]

        # Add line to file
        self.__logger.debug('Add point line to file: %s', str(point))
        self.__file.points.append(point)
