"""
Module for reading

History:
2020/08/21: v0.0.1
    + add cartography reader
"""

import logging
import re
from enum import Enum

import bca_config
import bca_utils
import mappings
from bca_types import CartographyPointCategory, CartographyRoom, CartographyPoint, CartographyInterestType


# __classes__ =====================================================================
class CartographyReader:
    """CSV/TSV cartography reader/parser"""

    # Types -------------------------------------------------------------------
    class __Mode(Enum):
        """Mode during read"""
        HEADER = 1
        ROOM = 2
        POINT = 3
        COMMENT = 4

    # Fields ------------------------------------------------------------------
    __logger = logging.getLogger('CartographyReader')

    # Constructor -------------------------------------------------------------
    def __init__(self, filepath):
        self.filepath = filepath
        self.__switcher = {
            self.__Mode.HEADER: self.__read_header,
            self.__Mode.ROOM: self.__read_room,
            self.__Mode.POINT: self.__read_point,
            self.__Mode.COMMENT: self.__read_comment
        }
        self.__separator = bca_config.tsv_separator

        self.__row = 0
        self.__column = 0
        self.__mode = CartographyReader.__Mode.HEADER

        self.__rooms = {}
        self.__point_names = []
        self.__room: CartographyRoom = None
        self.__pointCategory: CartographyPointCategory = None

    # Methods -----------------------------------------------------------------
    # Reading
    def read(self):
        with open(self.filepath, 'r', encoding='utf8') as file:
            for line in file:
                self.__row += 1
                line = line.strip()
                if not line:
                    self.__mode = self.__Mode.COMMENT
                    continue

                func = self.__switcher.get(self.__mode, None)
                if func is None:
                    raise ValueError('Invalid mode <' + self.__mode.name + '>')
                func(line)
        return self.__rooms

    def __read_header(self, line: str):
        self.__check_line(line, 'header', ['X', 'Y', 'Z', 'Observation.*'])
        self.__logger.debug('Header found!')
        self.__mode = self.__Mode.ROOM

    def __read_room(self, line: str):
        matches = self.__check_line(line, 'room', ['((Room|Salle) [0-9]+) ([A-Za-z].+)'])
        m = matches[0]
        self.__logger.debug('Room line found #%d', self.__row)

        # Get or create room
        name = m.group(1)
        room = self.__rooms.get(name, None)
        if room is None:
            self.__logger.debug('Create new room <%s>', name)
            room = CartographyRoom(name)
            self.__rooms[name] = room
        else:
            self.__logger.debug('Use existing room <%s>', name)
        self.__room = room

        # Get default point type for current room
        self.__column = 1
        self.__pointCategory = self.__check_point_category(m.group(3))
        self.__mode = self.__mode.POINT

    def __read_point(self, line: str):
        patterns = ['-?[0-9]+', '-?[0-9]+', '(-?[0-9]+)?', '([A-Za-z].+)?']
        matches = self.__check_line(line, 'point', patterns, False)
        if matches is None:
            try:
                self.__read_room(line)
            except:
                self.__raise_error(line, 'point or room', '|'.join(mappings.cartography_point_category.keys()) \
                                   + ' or ' + '|'.join(patterns))
        elif self.__room is not None:  # Always true in prod runtime
            self.__logger.debug('Point line found: #%d', self.__row)
            matches_count = len(matches)

            # Determine coordinates
            x = int(matches[0].group(0))
            y = int(matches[1].group(0))
            z = int(matches[2].group(0)) if matches_count > 2 and matches[2].group(0) else 0

            # Determine name, point type and sub type
            point_category = self.__pointCategory
            interest_type = None
            if matches_count > 3:
                name = matches[3].group(0)
                interest_type = self.__check_interest_type(name, interest_type)
                if interest_type is None:
                    point_category = self.__check_point_category(name, point_category)
            elif point_category is None:  # Always false in prod runtime
                raise Exception('Point line found but not the point type: #' + str(self.__row))
            else:
                name = self.__room.name + '_' + point_category.name

            # Check name is unique
            if name in self.__point_names:
                unique_name = name
                idx = 1
                while unique_name in self.__point_names:
                    unique_name = '{}_{:03d}'.format(name, idx)
                    idx += 1
                name = unique_name
            self.__point_names.append(name)

            # Create and add point to current room
            self.__logger.debug(
                'Create new point with params=<name:"%s", category:"%s", interest_type:%s x:%d, y:%d z:%d>'
                ' for room <%s>',
                name, point_category.name,
                '"{}"'.format(interest_type.name) if interest_type is not None else 'None',
                x, y, z,
                self.__room.name
            )
            point = CartographyPoint(name, point_category, x, y, z, interest_type)
            self.__room.points.append(point)
        else:
            raise Exception('Point line found but no room found')

    def __read_comment(self, line: str):
        self.__ignore_line(line)

    # Tools
    def __check_line(self, line: str, line_type: str, patterns: list, strict=True):
        data = line.split(self.__separator)
        matches = []
        columns = len([pattern for pattern in patterns if re.match('\\(.+\\)\\?', pattern)])
        count = max(len(data), columns)

        # Check number of columns
        if len(data) < count:
            if strict:
                self.__raise_error(line, line_type, self.__separator.join(patterns))
            return None

        # Check data
        for i in range(count):
            self.__column = i + 1
            pattern = patterns[i]
            value = data[i]
            m = re.match(pattern, value, re.IGNORECASE)
            if m is None:
                if strict:
                    self.__raise_error(value, line_type, pattern)
                return None
            matches.append(m)

        return matches

    def __check_point_category(self, value: str, default_value=None) -> CartographyPointCategory:
        for pattern, category in mappings.cartography_point_category.items():
            if bca_utils.match_around(pattern, value, re.IGNORECASE):
                return category
        if default_value is None:
            self.__raise_error(value, 'point type', '|'.join(mappings.cartography_point_category.keys()))
        return default_value

    @staticmethod
    def __check_interest_type(value: str, default_value=None) -> CartographyInterestType:
        for pattern, interest in mappings.cartography_interest_type.items():
            if bca_utils.match_around(pattern, value, re.IGNORECASE):
                return interest
        return default_value

    @staticmethod
    def __format_value(line: str) -> str:
        return line.replace('\n', '\\n') \
            .replace('\t', '\\t')

    def __ignore_line(self, line: str):
        self.__logger.info('Ignore <%s> (l.%d)', self.__format_value(line), self.__row)

    def __raise_error(self, value: str, inv_type: str, pattern: str):
        raise Exception(
            'Invalid %s: <%s> (l.%d, c.%d). Expected: <%s> (case insensitive)',
            inv_type, self.__format_value(value), self.__row, self.__column, pattern
        )


# [UN]REGISTER ================================================================
__classes__ = (
    # CartographyReader,
)
