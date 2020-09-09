"""
Module for parsing

History:
2020/09/01: v0.0.2
    + add cartography parser (copied from cartography reader and update for new TSV format)
"""

import logging
import os
import re
from copy import copy
from typing import Dict, List, Optional, Tuple

import bca_utils
import mappings
from bca_types import CartographyGroup, CartographyCategory, CartographyPoint, CartographyInterestType, \
    CartographyRoom
from reading import CartographyFile, CartographyFilePoint


# Classes =====================================================================
class CartographyParserException(Exception):
    # Constructor -------------------------------------------------------------
    def __init__(self, row: int, value: str, inv_type: str, pattern: str):
        Exception.__init__(self, 'Invalid {}: <{}> (l.{}). Expected: <{}> (case insensitive)'.format(
            inv_type,
            bca_utils.file_format_line_for_logging(value),
            row,
            pattern
        ))


class CartographyParser:
    """Cartography file parser"""

    # Types -------------------------------------------------------------------
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
            self.start: Optional[CartographyParser.__PointGroupTuple] = None  # noqa
            self.end: Optional[CartographyParser.__PointGroupTuple] = None  # noqa

    # Fields ------------------------------------------------------------------
    __logger: logging.Logger = logging.getLogger('CartographyParser')

    # Constructor -------------------------------------------------------------
    def __init__(self):
        self.__room: Optional[CartographyRoom] = None
        self.__row: int = 0
        self.__junctions: Dict[str, CartographyParser.__JunctionGroup] = {}

    # Methods -----------------------------------------------------------------
    # Reading
    def parse(self, file: CartographyFile):
        filename, extension = os.path.splitext(os.path.basename(file.path))
        self.__room = CartographyRoom(filename)
        self.__row = 0
        self.__junctions = {}

        # Read all point lines in file
        for line in file.points:
            self.__row = line.row
            self.__parse_point(line)

        # Post-treatment - Junctions
        self.__determinate_junctions()
        if len(self.__junctions) > 0:
            self.__update_groups_for_junctions()

        return self.__room

    def __parse_point(self, line: CartographyFilePoint):
        point = CartographyPoint()

        # Determine name and observations
        point.name = line.point_name
        if line.observations:
            point.name += ' (' + ', '.join(line.observations) + ')'
            point.observations = line.observations.copy()

        # Set location
        point.location = line.location

        # Get or create group
        group = self.__get_or_create_group(line)

        # Determine category and interest type
        category = group.category
        if line.observations:
            observations = ', '.join(line.observations)
            point.interest = self.__check_interest(observations)
            if point.interest is None:
                category, cat_match = self.__check_point_category(observations, point.category, [group.category])
        elif category is None:  # Always false in prod runtime
            raise Exception('Point line found but not the point type: #' + str(self.__row))
        point.category = category

        # Create and add point to current room
        self.__logger.debug('New point created: %s', str(point))
        group.points.append(point)

    def __get_or_create_group(self, line) -> CartographyGroup:
        name, category = self.__determinate_group_name_category(line)
        group = self.__room.groups.get(name, None)
        if group is None:
            self.__logger.debug('Create new group <%s>', name)
            group = CartographyGroup(name, category)
            self.__room.groups[name] = group

            if group.category.outline:
                if self.__room.outline_group is not None and self.__room.outline_group != group:
                    raise CartographyParserException(
                        self.__row,
                        group.name,
                        'group category',
                        'Only one outline for each room'
                    )
                self.__room.outline_group = group
        else:
            self.__logger.debug('Use existing group <%s>', name)
        return group

    def __determinate_group_name_category(self, line: CartographyFilePoint) -> Tuple[str, CartographyCategory]:
        categories = self.__parse_point_categories(', '.join(line.observations))
        if len(categories) > 1:
            category_types = [c for c, m in categories]
            if CartographyCategory.OUTLINE in category_types and CartographyCategory.GATE in category_types:
                category, cat_match = next((c, m) for c, m in categories if c == CartographyCategory.OUTLINE)
            else:
                category, cat_match = categories[0]
            self.__logger.warning(
                'Group - Multiple category found: <%s>. Use category: <%s>',
                ','.join([c.name for c, m in categories]),
                category
            )
        else:
            category, cat_match = categories[0]

        return cat_match.group(0), category

    # Junctions
    def __determinate_junctions(self):
        for group in self.__room.groups.values():
            for point in group.points:
                self.__determinate_junction(point, group)

    def __determinate_junction(self, ext_point: CartographyPoint, ext_group: CartographyGroup):
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
        category, cat_match = self.__check_point_category(partial_name)

        # Search group
        int_group = self.__find_group(partial_name, category, self.__room)
        if not int_group:
            self.__logger.warning('Junction group <%s> not found for point <%s>', partial_name, ext_point.name)
            return

        # Set junction start/end in group
        junction_group = bca_utils.dict_get_or_create(
            self.__junctions, int_group.name,
            lambda: CartographyParser.__JunctionGroup(self.__room, int_group)
        )
        if junction_group.start is None:
            self.__logger.debug('Junction group <%s>, start point found: %s', int_group.name, ext_point.name)
            junction_group.start = CartographyParser.__PointGroupTuple(ext_point, ext_group)
        elif junction_group.end is None:
            self.__logger.debug('Junction group <%s>, end point found: %s', int_group.name, ext_point.name)
            junction_group.end = CartographyParser.__PointGroupTuple(ext_point, ext_group)
        else:
            raise CartographyParserException(self.__row, ext_group.name, 'junction', '2 junctions: start and end')

    def __update_groups_for_junctions(self):
        for junction in self.__junctions.values():
            self.__check_junction(junction)
            self.__update_groups_for_junction(junction)

    def __check_junction(self, junction: __JunctionGroup):
        if junction.end is None:
            raise CartographyParserException(self.__row, junction.group.name, 'junction', '2 junctions: start and end')
        elif junction.start.point == junction.end.point:
            raise CartographyParserException(
                self.__row,
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
    @staticmethod
    def __parse_point_categories(value: str) -> List[Tuple[CartographyCategory, re.Match]]:
        """
        Parse value to extract point categories.

        :param value: Text to parse
        :return: List of categories found
        """
        categories = []
        for pattern, category in mappings.cartography_point_category.items():
            m = bca_utils.match_ignore_case(pattern, value, False)
            if m:
                categories.append((category, m))
        return categories

    def __check_point_category(
            self,
            value: str,
            dft_value: Optional[CartographyCategory] = None,
            categories_to_ignore: List[CartographyCategory] = ()
    ) -> Tuple[CartographyCategory, Optional[re.Match]]:
        """
        Get the first category that match with value.

        :param value: Value to parse
        :param dft_value: Default category to return if no category found (optional, None by default)
        :param categories_to_ignore: List of category to ignore (optional, empty list by default).
        NB: must be bypass if filtered categories is empty)
        :return: Tuple with category (required) and match result (optional)
        :raise CartographyParserException: No category found and default value is None
        """
        categories = self.__parse_point_categories(value)
        if categories:
            return bca_utils.list_next(((c, m) for c, m in categories if c not in categories_to_ignore), categories[0])
        elif dft_value is None:
            raise CartographyParserException(
                self.__row,
                value,
                'point category',
                '|'.join(mappings.cartography_point_category.keys())
            )
        return dft_value, None

    @staticmethod
    def __check_interest(value: str, dft_value: Optional[Tuple[CartographyInterestType, int]] = None) \
            -> Tuple[Optional[CartographyInterestType], int]:
        for pattern, interest in mappings.cartography_interest_type.items():
            # FIXME '(([0-9]+) )?' not working :(
            m = bca_utils.match_ignore_case('([0-9]+) ' + pattern, value, False)
            if m:
                return interest, int(m.group(1))
            m = bca_utils.match_ignore_case(pattern, value, False)
            if m:
                return interest, 1
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
            CartographyParser.__logger.warning('Too much group found for name <%s>: current=<%d> expected=<%d>',
                                               partial_name, count, 1)
            return None
        return groups[0] if count == 1 else None

    @staticmethod
    def __format_value(line: str) -> str:
        return line.replace('\n', '\\n') \
            .replace('\t', '\\t')

    @staticmethod
    def __normalize_z_axis(point: CartographyPoint, z: int) -> CartographyPoint:
        norm_point = copy(point)
        norm_point.location = copy(point.location)
        norm_point.location.z = z
        norm_point.copy = True
        return norm_point


# [UN]REGISTER ================================================================
__classes__ = (
    # CartographyParser,
)
