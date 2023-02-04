"""
Module for CSV reader
"""

import logging
import os
from typing import List
from typing import Optional

import utils
from config.patterns import TablePattern, ColumnModelCategory
from mathutils import Vector
from .common import CartographyReader
from .. import utils as read_utils
from ..exception import CartographyReaderException
from ..model import CartographyFile, CartographyFileInfo, CartographyFileLine, CartographyFilePoint, \
    CartographyFileSide, ReadContext


# CLASSES =====================================================================
class CartographyCsvReader(CartographyReader):
    """CSV cartography reader"""

    # Types -------------------------------------------------------------------
    class Patterns:
        """Patterns to use for parse/check lines"""

        def __init__(self, model):
            self.header_extras: List[List[str]] = [
                ['' if h.ignore else h.pattern for i, h in enumerate(hs)] for hs in model.headers
            ]
            self.header_extra_names: List[List[str]] = [
                [h.name or f'c{i:02}' for i, h in enumerate(hs)] for hs in model.headers
            ]

            self.point_header: List[str] = ['' if c.ignore else c.header for c in model.columns]
            self.point_data: List[str] = ['' if c.ignore else c.pattern for c in model.columns]
            self.point_names: List[str] = [c.name or f'c{i:02}' for i, c in enumerate(model.columns)]
            self.point_data_names: List[str] = [c.name for i, c in enumerate(model.columns)]
            self.point_has_coordinates: bool = ColumnModelCategory.COORDINATE in [c.category for c in model.columns]

    # Fields ------------------------------------------------------------------
    __logger: logging.Logger = logging.getLogger('CartographyCsvReader')

    # Constructor -------------------------------------------------------------
    def __init__(self, separator: str, model: TablePattern):
        # General
        self.__separator = separator
        self.__model = model
        self.__patterns = CartographyCsvReader.Patterns(model)

        # Execution (reset before each execution)
        self.__file: Optional[CartographyFile] = None
        self.__header: bool = True
        self.__headers_found: List[bool] = []
        self.__last_point_side = None

    # Methods -----------------------------------------------------------------
    # Reading
    def read(self, filepath: os.path) -> CartographyFile:
        # Reset execution variables
        self.__file = CartographyFile(filepath)
        self.__header = True
        self.__headers_found = [False] * len(self.__model.headers)
        self.__last_point_side = None

        context = ReadContext(self.__separator, self.__logger)

        # Read all lines in CSV file
        with open(filepath, 'r', encoding='utf8') as file:
            for line in file:
                context.row += 1
                if not line.strip():
                    continue
                elif line.startswith('#'):
                    read_utils.line.ignore(context, line)
                    continue
                elif self.__header:
                    self.__read_header(context, line)
                    continue
                else:
                    self.__read_point(context, line)

            # Check if a point found
            if self.__header:
                raise CartographyReaderException(
                    context.row,
                    context.column,
                    'Only header was found!',
                    'header',
                    'A line of type "point"'
                )

        # Collect information from data
        info = CartographyFileInfo(context.row, line)
        info.s1s2_distance = int(context.data['dist_s1_s2'])
        info.scribes1 = context.data['scribe_1'].split(', ?')
        info.scribes2 = context.data['scribe_2'].split(', ?')
        info.explorers = context.data['explorer'].split(', ?')
        self.__file.info = info

        return self.__file

    def __read_header(self, context: ReadContext, line: str):
        self.__file.headers.append(CartographyFileLine(context.row, line))

        if not self.__read_header_extra(context, line):
            self.__read_header_extra_finish_check()
            if self.__read_header_point(context, line):
                self.__header = False

    def __read_header_extra(self, context: ReadContext, line: str) -> bool:
        headers = self.__model.headers
        for i, header in enumerate(headers):
            patterns = self.__patterns.header_extras[i]
            names = self.__patterns.header_extra_names[i]
            matches = read_utils.line.check(context, line, 'header_extra', patterns, names, False, True, False)
            if matches:
                if self.__headers_found[i]:
                    self.__logger.warning('Header #%d is already found. Ignored', context.row)
                    return True

                self.__logger.debug('Header #%d is found: %s', context.row, utils.io.file.format_line_for_logging(line))
                for index, column in enumerate(header):
                    if column.name:
                        value = matches[index].group(0)
                        self.__logger.debug(
                            'Header #%d, column #%d - data retrieved: %s=%s',
                            context.row, index + 1, column.name, value
                        )
                        context.data[column.name] = value
                self.__headers_found[i] = True
                return True
        return False

    def __read_header_extra_finish_check(self):
        headers_not_found = []
        total = len(self.__headers_found)
        for i, found in enumerate(self.__headers_found):
            if not found:
                headers_not_found.append(i)
        if len(headers_not_found) > 0:
            self.__logger.warning(
                '%d/%d header(s) not found: [%s]',
                len(headers_not_found),
                total,
                ', '.join(map(lambda idx: str(idx), headers_not_found))
            )
        else:
            self.__logger.debug('%d/%d extra headers found!', total, total)

    def __read_header_point(self, context: ReadContext, line: str) -> bool:
        # Check point headers for get column indexes
        patterns = self.__patterns.point_header
        names = self.__patterns.point_names
        if read_utils.line.check(context, line, 'header_point', patterns, names, False, True):
            self.__logger.debug('Header of point table found on line #%d', context.row)
            return True

        self.__logger.warning(
            'Header of line #%d not identified: %s',
            context.row, utils.io.file.format_line_for_logging(line)
        )
        return False

    def __read_point(self, context: ReadContext, line: str):
        # Check line data
        patterns = self.__patterns.point_data
        names = self.__patterns.point_names
        matches = read_utils.line.check(context, line, 'point', patterns, names, False, True)
        if not matches:
            read_utils.line.ignore(context, line)
            return

        # FIXME find a better way
        # Check data found (point name must be filled without data associated, just ignore this case)
        excluded_indexes = [i for i, c in enumerate(self.__model.columns)
                            if c.ignore or c.category == ColumnModelCategory.COORDINATE]
        data_found = sum(1 for i, m in enumerate(matches) if m and m.group(0) and i not in excluded_indexes)
        if data_found <= 1:
            read_utils.line.ignore(context, line)
            return

        # Retrieve and check data from line
        data_names = self.__patterns.point_data_names
        data_map = read_utils.line.extract_data_map(context, line, data_names)

        # Create a new point
        self.__logger.debug('Line #%d: point found! (%s)', context.row, utils.io.file.format_line_for_logging(line))
        point = CartographyFilePoint(context.row, line)

        # Determine information
        point.point_name = data_map['point_name'].value

        # Determine statements
        point.s1_distance = data_map['dist_s1'].value_to_int()
        point.s2_distance = data_map['dist_s2'].value_to_int()
        point.height = data_map['height'].value_to_float()

        # FIXME check here of after ?
        if point.s1_distance == 0 and point.s2_distance == 0 and point.height == 0:
            raise CartographyReaderException(
                context.row,
                context.column,
                '',
                'point statement (distances, height)',
                'not_all_blank'
            )

        # Determine point side
        side = data_map['side'].value
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
            raise CartographyReaderException(
                context.row,
                context.column,
                '',
                'point side',
                '[DGRL]'
            )
        self.__last_point_side = point.side

        # Determine global type of point
        required_data_not_found = ['category']

        category = data_map['category'].value
        if category:
            point.category = category
            point.group_identifier = data_map['group_identifier'].value_to_int()
            required_data_not_found.remove('category')

        interest_type = data_map['interest_type'].value
        if interest_type:
            point.interest_type = interest_type

        # FIXME check here of after ?
        if len(required_data_not_found) > 0:
            self.__logger.error(
                'Required data not found in line #%d: %s',
                context.row, utils.io.file.format_line_for_logging(line)
            )
            raise CartographyReaderException(
                context.row,
                context.column,
                '',
                'point category',
                'not_all_blank'
            )

        point.observations = data_map['observations'].value

        # Determine coordinates
        location = Vector((0, 0, 0))
        if self.__patterns.point_has_coordinates:
            location = Vector((
                data_map['loc_x'].value_to_float(),
                data_map['loc_y'].value_to_float(),
                data_map['loc_z'].value_to_float()
            ))
        point.location = location

        # Add line to file
        self.__logger.debug('Add point line to file: %s', str(point))
        self.__file.points.append(point)
