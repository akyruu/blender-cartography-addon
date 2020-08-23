"""
Module for reading

History:
2020/08/21: v0.0.1
    + add cartography reader
"""

import logging
import os
import re
from copy import copy
from enum import Enum
from typing import Dict, Callable, List, Optional, Tuple

from mathutils import Vector

import bca_config
import bca_utils
import mappings
from bca_types import CartographyGroup, CartographyCategory, CartographyPoint, CartographyInterestType, \
    CartographyRoom


# __classes__ =====================================================================
class CartographyReader:
    """CSV/TSV cartography reader/parser"""

    # Types -------------------------------------------------------------------
    class __Mode(Enum):
        """Mode during read"""
        HEADER = 1
        ROOM_AND_GROUP = 2
        POINT = 3
        COMMENT = 4

    class __PointGroupTuple:
        """Tuple with point and group"""

        def __init__(self, point: CartographyPoint, group: CartographyGroup):
            self.point = point
            self.group = group

    class __JunctionGroup:
        """Junction between two points"""

        def __init__(self, room: CartographyRoom, group: CartographyGroup):
            self.room = room
            self.group = group
            self.start: Optional[CartographyReader.__PointGroupTuple] = None  # noqa
            self.end: Optional[CartographyReader.__PointGroupTuple] = None  # noqa

    # Fields ------------------------------------------------------------------
    __logger: logging.Logger = logging.getLogger('CartographyReader')

    # Constructor -------------------------------------------------------------
    def __init__(self, filepath: os.path):
        # Configuration
        self.filepath: os.path = filepath
        self.__switcher: Dict[CartographyReader.__Mode, Callable[[str], None]] = {
            CartographyReader.__Mode.HEADER: self.__read_header,
            CartographyReader.__Mode.ROOM_AND_GROUP: self.__read_room_and_group,
            CartographyReader.__Mode.POINT: self.__read_point,
            CartographyReader.__Mode.COMMENT: self.__read_comment
        }
        self.__separator: str = bca_config.tsv_separator

        # Read variables
        self.__row: int = 0
        self.__column: int = 0
        self.__mode: CartographyReader.__Mode = CartographyReader.__Mode.HEADER

        # Entity variables
        self.__rooms: Dict[str, CartographyRoom] = {}
        self.__point_names: List[str] = []
        self.__room: Optional[CartographyRoom] = None
        self.__group: Optional[CartographyGroup] = None
        self.__junctions: Dict[str, CartographyReader.__JunctionGroup] = {}

    # Methods -----------------------------------------------------------------
    # Reading
    def read(self):
        # Read all lines in file
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

        # Post-treatment - Junctions
        self.__determinate_junctions()
        if len(self.__junctions) > 0:
            self.__update_groups_for_junctions()

        return self.__rooms

    def __read_header(self, line: str):
        self.__check_line(line, 'header', ['X', 'Y', 'Z', 'Observation.*'])
        self.__logger.debug('Header found!')
        self.__mode = self.__Mode.ROOM_AND_GROUP

    def __read_room_and_group(self, line: str):
        matches = self.__check_line(line, 'room', ['((Room|Salle) [0-9]+) ([A-Za-z].+)'])
        m = matches[0]
        self.__logger.debug('Room line found #%d', self.__row)

        # Get or create room
        room_name = m.group(1)
        room = self.__rooms.get(room_name, None)
        if room is None:
            self.__logger.debug('Create new room <%s>', room_name)
            room = CartographyRoom(room_name)
            self.__rooms[room_name] = room
        else:
            self.__logger.debug('Use existing room <%s>', room_name)
        self.__room = room

        # Get or create group
        group_name = m.group(0).strip(' :')
        group = room.groups.get(group_name, None)
        if group is None:
            self.__logger.debug('Create new group <%s>', group_name)
            group = CartographyGroup(group_name, self.__check_point_category(m.group(3)))
            room.groups[group_name] = group

            if group.category.outline:
                if room.outline_group is not None:
                    self.__raise_error(group.name, 'group category', 'Only one outline for each room')
                room.outline_group = group
        else:
            self.__logger.debug('Use existing group <%s>', group_name)
        self.__group = group

        # Reset column and update read mode
        self.__column = 1
        self.__mode = self.__mode.POINT

    def __read_point(self, line: str):
        patterns = ['-?[0-9]+', '-?[0-9]+', '(-?[0-9]+)?', '([A-Za-z0-9].+)?']
        matches = self.__check_line(line, 'point', patterns, False)
        if matches is None:
            try:
                self.__read_room_and_group(line)
            except:  # noqa
                self.__raise_error(line, 'point or room', '|'.join(mappings.cartography_point_category.keys()) \
                                   + ' or ' + '|'.join(patterns))
        elif self.__room is not None:  # Always true in prod runtime
            self.__logger.debug('Point line found: #%d', self.__row)
            matches_count = len(matches)

            # Determine coordinates
            location = Vector((
                int(matches[0].group(0)),
                int(matches[1].group(0)),
                int(matches[2].group(0)) if matches_count > 2 and matches[2].group(0) else 0
            ))

            # Determine name, point type and sub type
            category = self.__group.category
            interest = None
            observations = []
            if matches_count > 3:
                name = matches[3].group(0)
                interest = self.__check_interest(name, interest)
                if interest is None:
                    category = self.__check_point_category(name, category)
                observations = name.split(bca_config.obs_separator)
            elif category is None:  # Always false in prod runtime
                raise Exception('Point line found but not the point type: #' + str(self.__row))
            else:
                name = self.__group.name

            # Check name is unique
            if name in self.__point_names:
                unique_name = name
                idx = 1
                while unique_name in self.__point_names:
                    unique_name = '{}{}{:03d}'.format(name, mappings.cartography_point_name_join, idx)
                    idx += 1
                name = unique_name
            self.__point_names.append(name)

            # Create and add point to current room
            point = CartographyPoint(name, category, location, observations, interest)
            self.__logger.debug('New point created: %s', str(point))
            self.__group.points.append(point)
        else:
            raise Exception('Point line found but no room found')

    def __read_comment(self, line: str):
        self.__ignore_line(line)

    # Junctions
    def __determinate_junctions(self):
        for room in self.__rooms.values():
            for group in room.groups.values():
                for point in group.points:
                    self.__determinate_junction(point, group, room)

    def __determinate_junction(self, ext_point: CartographyPoint, ext_group: CartographyGroup, room: CartographyRoom):
        # Search observation sentence
        match = None
        for observation in ext_point.observations:
            m = bca_utils.match_ignore_case(mappings.cartography_junction_pattern, observation, False)
            if m:
                match = m
                break
        if not match:
            return

        # Determinate point attributes to search
        partial_name = match.group(2)  # 1: junction word, 2: category (with optional number)
        category = self.__check_point_category(partial_name)

        # Search group
        int_group = self.__find_group(partial_name, category, room)
        if not int_group:
            self.__logger.warning('Junction group <%s> not found for point <%s>', int_group.name, ext_point.name)
            return

        # Set junction start/end in group
        junction_group = bca_utils.dict_get_or_create(
            self.__junctions, int_group.name,
            lambda: CartographyReader.__JunctionGroup(room, int_group)
        )
        if junction_group.start is None:
            self.__logger.debug('Junction group <%s>, start point found: %s', int_group.name, ext_point.name)
            junction_group.start = CartographyReader.__PointGroupTuple(ext_point, ext_group)
        elif junction_group.end is None:
            self.__logger.debug('Junction group <%s>, end point found: %s', int_group.name, ext_point.name)
            junction_group.end = CartographyReader.__PointGroupTuple(ext_point, ext_group)
        else:
            self.__raise_error(ext_group.name, 'junction', '2 junctions: start and end')

    def __update_groups_for_junctions(self):
        for junction in self.__junctions.values():
            self.__check_junction(junction)
            self.__update_groups_for_junction(junction)

    def __check_junction(self, junction: __JunctionGroup):
        if junction.end is None:
            self.__raise_error(junction.group.name, 'junction', '2 junctions: start and end')
        elif junction.start.point == junction.end.point:
            self.__raise_error(
                '{}.points=[start=end={}]'.format(junction.group.name, junction.start.point.name),
                'junction',
                'Start point different of end point'
            )
        elif junction.start.group != junction.end.group:
            raise Exception('##TODO## start/end junction group is different')  # TODO
        elif not junction.start.group.category.outline:
            raise Exception('##TODO## junction group with another of outline')  # TODO

    def __update_groups_for_junction(self, junction: __JunctionGroup):
        # Update groups
        int_group = junction.group
        int_points = int_group.points
        ext_group = junction.start.group
        ext_points = ext_group.points

        self.__logger.debug('Update groups for junction group <%s>...', int_group.name)
        try:
            # Split external points
            fst_ext_points: list = bca_utils.list_sublist(ext_points, 0, junction.start.point)
            mid_ext_points: list = bca_utils.list_sublist(ext_points, junction.start.point, (junction.end.point, 1))
            lst_ext_points: list = bca_utils.list_sublist(ext_group.points, (junction.end.point, 1))

            # Update external points
            ext_points.clear()
            ext_points += fst_ext_points

            ext_to_add_points = [junction.start.point] + int_points + [junction.end.point]
            ext_z = fst_ext_points[-2].location.z if len(fst_ext_points) > 1 \
                else (lst_ext_points[1].location.z if len(lst_ext_points) > 1
                      else None)
            if ext_z is not None and int_points[0].location.z != ext_z:
                ext_to_add_points = [self.__normalize_z_axis(p, ext_z) for p in ext_to_add_points]
            ext_points += ext_to_add_points

            ext_points += lst_ext_points
            self.__logger.debug(
                '<%d> points transferred from group <%s> to <%s>',
                len(int_points), int_group.name, ext_group.name
            )

            # Update internal points
            int_points += bca_utils.list_reverse(mid_ext_points)  # Reverse for keep order in new group
            self.__logger.debug(
                '<%d> points transferred from group <%s> to <%s>',
                len(mid_ext_points), ext_group.name, int_group.name)
        except ValueError as err:
            self.__logger.error('Failed to update groups for junction group <%s>', int_group.name, exc_info=err)

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
            m = bca_utils.match_ignore_case(pattern, value)
            if m is None:
                if strict:
                    self.__raise_error(value, line_type, pattern)
                return None
            matches.append(m)

        return matches

    def __check_point_category(self, value: str, dft_value=None) -> CartographyCategory:
        for pattern, category in mappings.cartography_point_category.items():
            if bca_utils.match_ignore_case(pattern, value, False):
                return category
        if dft_value is None:
            self.__raise_error(value, 'point category', '|'.join(mappings.cartography_point_category.keys()))
        return dft_value

    @staticmethod
    def __check_interest(value: str, dft_value: Optional[Tuple[CartographyInterestType, int]] = None) \
            -> Tuple[Optional[CartographyInterestType], int]:
        for pattern, interest in mappings.cartography_interest_type.items():
            m = bca_utils.match_ignore_case('(([0-9]+) )?' + pattern, value, False)
            if m:
                return interest, int(m.group(2)) if m.group(2) else 1
        return dft_value

    @staticmethod
    def __find_group(
            partial_name: str,
            category: CartographyCategory,
            room: CartographyRoom
    ) -> Optional[CartographyGroup]:
        groups = [
            g for g in room.groups.values()
            if g.category == category and bca_utils.match_ignore_case(partial_name, g.name, False)
        ]
        count = len(groups)
        if count > 1:
            CartographyReader.__logger.warning('Too much group found for name <%s>: current=<%d> expected=<%d>',
                                               partial_name, count, 1)
            return None
        return groups[0] if count == 1 else None

    @staticmethod
    def __format_value(line: str) -> str:
        return line.replace('\n', '\\n') \
            .replace('\t', '\\t')

    def __ignore_line(self, line: str):
        self.__logger.info('Ignore <%s> (l.%d)', self.__format_value(line), self.__row)

    @staticmethod
    def __normalize_z_axis(point: CartographyPoint, z: int) -> CartographyPoint:
        norm_point = copy(point)
        norm_point.location = copy(point.location)
        norm_point.location.z = z
        norm_point.copy = True
        return norm_point

    def __raise_error(self, value: str, inv_type: str, pattern: str):
        raise Exception(
            'Invalid %s: <%s> (l.%d, c.%d). Expected: <%s> (case insensitive)',
            inv_type, self.__format_value(value), self.__row, self.__column, pattern
        )


# [UN]REGISTER ================================================================
__classes__ = (
    # CartographyReader,
)
