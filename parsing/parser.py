"""
Module for parser
"""

import logging
import os
import re
from typing import List, Tuple

import mappings
import utils
from model import CartographyCategory, CartographyGroup, CartographyPoint, CartographyRoom
from reading import CartographyFile, CartographyFilePoint
from utils.collection import dict as dict_utils
from . import utils as parse_utils
from .exception import CartographyParserException
from .model import ParseContext


# TODO split this parser in multiple sub classes (remove utils for move to classes ?)
# CLASSES =====================================================================
class CartographyParser:
    """Cartography file parser"""

    # Fields ------------------------------------------------------------------
    __logger: logging.Logger = logging.getLogger('CartographyParser')

    # Constructor -------------------------------------------------------------
    def __init__(self):
        self.__context = ParseContext(self.__logger)

    # Methods -----------------------------------------------------------------
    def parse(self, file: CartographyFile) -> CartographyRoom:
        filename, extension = os.path.splitext(os.path.basename(file.path))
        self.__context.room = CartographyRoom(filename)
        self.__context.row = 0
        self.__context.junctions = {}

        # Read all point lines in file
        for line in file.points:
            self.__context.row = line.row
            self.__parse_point(line)

        # Post-treatments
        self.__treat_group_links(self.__context.room)

        # PT - Junctions @deprecated
        parse_utils.junction_old.determinate_junctions(self.__context)
        if len(self.__context.junctions) > 0:
            parse_utils.junction_old.update_groups_for_junctions(self.__context)

        return self.__context.room

    def __parse_point(self, file_point: CartographyFilePoint):
        categories = parse_utils.category.parse_categories(file_point.observations, True)

        # Create one point for each category found in file point
        groups_points: List[Tuple[CartographyGroup, CartographyPoint]] = []
        for category, cat_match in categories:
            group_point = self.__parse_point_item(file_point, categories, cat_match)
            groups_points.append(group_point)

        # Create junctions
        parse_utils.junction.create_junctions(self.__context, groups_points)

    # Points
    def __parse_point_item(
            self,
            file_point: CartographyFilePoint,
            categories: List[Tuple[CartographyCategory, re.Match]],
            cat_match: re.Match
    ) -> Tuple[CartographyGroup, CartographyPoint]:
        point = CartographyPoint()

        # Set properties
        observation = cat_match.group(0)
        point.name = file_point.point_name
        point.comments = [observation]
        point.location = file_point.location
        point.observations = [observation]

        # Get or create group
        group = parse_utils.group.get_or_create(self.__context, point.observations)

        # Determine category and interest type
        point.category = CartographyCategory.UNKNOWN
        category = group.category
        point.interest = parse_utils.common.check_interest(observation)
        if point.interest is None:
            category, cat_match = parse_utils.category.parse_point_category(
                self.__context,
                file_point.observations,
                point.category,
                [group.category]
            )
        elif category is None:  # Always false in prod runtime
            raise CartographyParserException('Point line found but not the point type: #' + str(self.__context.row))
        point.category = category

        # Determine additional categories
        point.additional_categories = [c for c, m in categories if c != category]
        self.__add_category_if_not_exists(point, group.category)
        if point.has_category(CartographyCategory.GATE):
            self.__add_category_if_not_exists(point, CartographyCategory.OUTLINE)

        # Create and add point to current room
        self.__context.logger.debug('New point created: %s', str(point))
        group.points.append(point)

        return group, point

    @staticmethod
    def __add_category_if_not_exists(point: CartographyPoint, category: CartographyCategory):
        if category != point.category and category not in point.additional_categories:
            point.additional_categories.append(category)

    # Post-treatments
    def __treat_group_links(self, room: CartographyRoom):
        # TODO automatize from category description ?
        for group in [g for g in room.groups.values() if g.category == CartographyCategory.COLUMN_BASE]:
            group_name = group.name

            pattern = dict_utils.get_key(mappings.cartography_point_category, CartographyCategory.COLUMN)
            match = utils.string.match_ignore_case('(' + pattern + ')', group_name, False)
            if match:
                linked_name = match.group(1).capitalize()
                linked_group = room.groups[linked_name]
                if linked_group:
                    self.__logger.debug('Column found <%s> for base <%s>', linked_name, group_name)
                    group.linked.append(linked_group)
                else:
                    self.__logger.warning('Column not found for column: <%s>', linked_group)
            else:
                self.__logger.warning('Column group name not found for base: <%s>', group_name)
