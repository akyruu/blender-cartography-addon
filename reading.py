"""
Module for reading

History:
2020/08/21: v0.0.1
    + add cartography reader
2020/09/01: v0.0.2
    + separate parsing in a different module
    + add cartography line
    + update cartography reader for new TSV sample (format: test -> real carto)
"""

import logging
import os
import re
from abc import abstractmethod
from enum import Enum
from typing import List, Optional

from mathutils import Vector

import bca_config
import bca_utils


# CLASSES =====================================================================
# File ------------------------------------------------------------------------
class CartographyFileLine:
    """Line in cartography file"""

    # Constructor -------------------------------------------------------------
    def __init__(self, row: int, text: str):
        self.row = row
        self.text = text

    # Methods -----------------------------------------------------------------
    def __repr__(self):
        return bca_utils.object_to_repr(self)

    def __str__(self):
        return bca_utils.object_to_str(self)


class CartographyFileSide(Enum):
    """Side of point line in cartography file"""
    LEFT = 1
    RIGHT = 2
    UNKNOWN = 3


class CartographyFilePoint(CartographyFileLine):
    """Point line in cartography file"""

    # Constructor -------------------------------------------------------------
    def __init__(
            self,
            row: int,
            text: str,
            location: Vector = Vector((0, 0, 0)),
            observations: List[str] = (),
            point_name: str = '',
            side: CartographyFileSide = None,
            s1_distance: int = 0,
            s2_distance: int = 0,
            height: int = 0,
    ):
        CartographyFileLine.__init__(self, row, text)
        self.location = location
        self.observations = observations
        self.point_name = point_name
        self.side = side
        self.s1_distance = s1_distance
        self.s2_distance = s2_distance
        self.height = height

    # Methods -----------------------------------------------------------------
    def __repr__(self):
        return bca_utils.object_to_repr(self)

    def __str__(self):
        return bca_utils.object_to_str(self)


class CartographyFile:
    """Cartography file"""

    # Constructor -------------------------------------------------------------
    def __init__(self, filepath: os.path):
        self.path = filepath
        self.headers: List[CartographyFileLine] = []
        self.points: List[CartographyFilePoint] = []

    # Methods -----------------------------------------------------------------
    def __repr__(self):
        return bca_utils.object_to_repr(self)

    def __str__(self):
        return bca_utils.object_to_str(self)


# Reader ----------------------------------------------------------------------
class CartographyReader:
    """Interface for cartography readers"""

    # Methods -----------------------------------------------------------------
    @abstractmethod
    def read(self, filepath: os.path) -> CartographyFile:
        pass

    @abstractmethod
    def row(self) -> int:
        pass

    @abstractmethod
    def column(self) -> int:
        pass


class CartographyReaderException(Exception):
    # Constructor -------------------------------------------------------------
    def __init__(self, reader: CartographyReader, value: str, inv_type: str, pattern: str):
        Exception.__init__(self, 'Invalid {}: <{}> (l.{}, c.{}). Expected: <{}> (case insensitive)'.format(
            inv_type,
            bca_utils.file_format_line_for_logging(value),
            reader.row(),
            reader.column(),
            pattern
        ))


class AbstractCartographyReader(CartographyReader):
    """Abstraction for cartography readers"""

    # Constructor -------------------------------------------------------------
    def __init__(self):
        self._row: int = 0
        self._column: int = 0

    # Methods -----------------------------------------------------------------
    @abstractmethod
    def read(self, filepath: os.path) -> CartographyFile:
        pass

    def row(self) -> int:
        return self._row

    def column(self) -> int:
        return self._column


class CartographyCsvReader(AbstractCartographyReader):
    """CSV cartography reader"""

    # Fields ------------------------------------------------------------------
    __logger: logging.Logger = logging.getLogger('CartographyCsvReader')

    # Constructor -------------------------------------------------------------
    def __init__(self, separator: str):
        # Configuration
        self.__separator = separator

        # Read variables
        self.__file: Optional[CartographyFile] = None
        self.__header: bool = True
        self.__last_point_side = None

    # Methods -----------------------------------------------------------------
    # Reading
    def read(self, filepath: os.path) -> CartographyFile:
        self.__file = CartographyFile(filepath)
        self.__header = True
        self._row = 0
        self._column = 0

        with open(filepath, 'r', encoding='utf8') as file:
            # Read all lines in CSV file
            for line in file:
                self._row += 1
                line = line.strip()
                if not line:
                    continue
                elif line.startswith('#'):
                    self.__ignore_line(line)
                    continue
                elif self.__header:
                    self.__read_header(line)
                else:
                    self.__read_point(line)

            # Check if a point found
            if self.__header:
                raise CartographyReaderException(self, 'Only header was found!', 'header', 'A line of type "point"')

        return self.__file

    def __read_header(self, line: str):
        self.__file.headers.append(CartographyFileLine(self._row, line))
        if self.__check_line(line, 'header', [
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

    def __read_point(self, line: str):
        # Check line describe a point
        patterns = [
            'point [0-9]+',  # Point name (0)
            '[DGRL]?',  # Side (1)
            '([0-9]+)?',  # Distance to S1 (2)
            '([0-9]+)?',  # Distance to S2 (3)
            '([0-9]+)?',  # Height (4)
            '([A-Za-z0-9].+)', '', '',  # Observations (5)
            '-?[0-9]+', '',  # Y (8)
            '-?[0-9]+', '',  # X (10)
            '-?[0-9]+', '', '', '', '',  # Z (12)
            '(.+)?'  # Adjacent Y (17)
        ]
        matches = self.__check_line(line, 'point', patterns, False)
        if not matches:
            matches = self.__check_line(line, 'point', ['point [0-9]+'], False)
            if not matches:
                raise CartographyReaderException(self, line, 'point', '|'.join(patterns))
            self.__ignore_line(line)
            return

        # Create a new point
        self.__logger.debug('Point line found: #%d', self._row)
        point = CartographyFilePoint(self._row, line)

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
        elif bca_utils.match_ignore_case('[GL]', side):
            point.side = CartographyFileSide.LEFT
        elif bca_utils.match_ignore_case('[DR]', side):
            point.side = CartographyFileSide.RIGHT

        if not point.side:
            raise CartographyReaderException(self, side, 'point side', '[DGRL]')
        self.__last_point_side = point.side

        # Determine observations
        observations = matches[5].group(0)
        if observations:
            point.observations = [o.strip() for o in observations.split(bca_config.obs_separator)]

        # Add line to file
        self.__logger.debug('Add point line to file: %s', str(point))
        self.__file.points.append(point)

    # Tools
    def __check_line(self, line: str, line_type: str, patterns: list, strict=True):
        matches = []

        # Split line
        data = line.split(self.__separator)
        data_count = len(data)

        # Determine columns count
        patterns_count = len(patterns)
        columns = patterns_count
        while columns > 0 and (not patterns[columns - 1] or re.match('\\(.+\\)\\?', patterns[columns - 1])):
            columns -= 1
        count = min(max(data_count, columns), patterns_count)

        # Check number of columns
        if data_count < count:
            if strict:
                self._column = 1
                raise CartographyReaderException(self, line, line_type, self.__separator.join(patterns))
            return None
        elif data_count > count:
            self.__logger.warning('Data ignored for line "<%s>": current=<%d>, expected=<%d>', line, data_count, count)

        # Check data
        for i in range(count):
            self._column = i + 1
            pattern = patterns[i] if patterns[i] else '^$'
            value = data[i]
            m = bca_utils.match_ignore_case(pattern, value)
            if m is None:
                if strict:
                    raise CartographyReaderException(self, value, line_type, pattern)
                return None
            matches.append(m)

        return matches

    def __ignore_line(self, line: str):
        self.__logger.info('Ignore <%s> (l.%d)', bca_utils.file_format_line_for_logging(line), self._row)


class CartographyTsvReader(CartographyCsvReader):
    """TSV cartography reader"""

    # Constructor -------------------------------------------------------------
    def __init__(self):
        CartographyCsvReader.__init__(self, '\t')


# [UN]REGISTER ================================================================
__classes__ = (
    # CartographyFileSide,
    # CartographyFilePoint,
    # CartographyFile,
    # CartographyReader,
    # CartographyCsvReader
    # CartographyTsvReader
)
