"""
Module for parser
"""

import logging
import os
from typing import List, Tuple, Optional

import mappings
import utils
from model import CartographyCategory, CartographyGroup, CartographyPoint, CartographyRoom
from reading import CartographyFile, CartographyFilePoint
from . import utils as parse_utils
from .exception import CartographyParserException
from .model import ParseContext


# TODO split this parser in multiple sub classes (remove utils for move to classes ?)
# CLASSES =====================================================================
class CartographyParser:
    """Cartography file parser"""

    # Fields ------------------------------------------------------------------
    __logger: logging.Logger = logging.getLogger('CartographyParser')

    # Methods -----------------------------------------------------------------
    def parse(self, file: CartographyFile) -> CartographyRoom:
        filename, extension = os.path.splitext(os.path.basename(file.path))
        context = ParseContext(CartographyRoom(filename), self.__logger)

        # Read all point lines in file
        for file_point in file.points:
            context.row = file_point.row
            self.__parse_point(context, file_point)

        # Post-treatments
        self.__treat_group_links(context.room)

        # PT - Junctions @deprecated
        #parse_utils.junction_old.determinate_junctions(context)
        #if len(context.junctions) > 0:
        #    parse_utils.junction_old.update_groups_for_junctions(context)

        return context.room

    def __parse_point(self, context: ParseContext, file_point: CartographyFilePoint):
        # Create one point for each category found in file point
        groups_points: List[Tuple[CartographyGroup, CartographyPoint]] = []
        group_point = self.__parse_point_item(context, file_point)
        if group_point:
            groups_points.append(group_point)
            parse_utils.junction.create_junctions(context, groups_points)  # Create junctions

    # Points
    def __parse_point_item(
            self,
            context: ParseContext,
            file_point: CartographyFilePoint
    ) -> Tuple[CartographyGroup, Optional[CartographyPoint]]:
        point = CartographyPoint()

        # Set properties
        point.name = file_point.point_name
        point.comments = [file_point.observations]
        point.location = file_point.location
        point.observations = [file_point.observations]

        # Set category (+extra) and interest type
        category_name = file_point.category
        if category_name:
            category = next(
                (cat
                 for pattern, cat in mappings.cartography_point_category.items()
                 if utils.string.match_ignore_case(pattern, category_name))
                , None)
            if not category:
                raise CartographyParserException(context.row, f'Category <{category_name}> not found')
            point.category = category
        else:
            point.category = CartographyCategory.UNKNOWN
        self.__add_extra_category_if_not_exists(point, point.category)

        point.interest = parse_utils.common.check_interest(file_point.interest_type or '')

        if not point.category and not point.interest:
            raise CartographyParserException(context.row, 'Point found but not the point category/interest type')

        if point.category == CartographyCategory.GATE:
            self.__add_extra_category_if_not_exists(point, CartographyCategory.OUTLINE)

        # Get or create group
        group_category = point.category
        if group_category == CartographyCategory.GATE:
            group_category = CartographyCategory.OUTLINE
        group = parse_utils.group.get_or_create(context, group_category, file_point.category_number)

        self.__add_extra_category_if_not_exists(point, group_category)

        # Check if point already exist
        existing_point = next((p for p in group.points if p.location == point.location), None)
        if existing_point:
            extra_categories = point.extra_categories
            missing_categories = [c for c in extra_categories if c not in existing_point.extra_categories]
            if missing_categories:
                self.__logger.debug(
                    'Point already exist: %s. Add missing categories: %s',
                    str(existing_point),
                    ', '.join(c.name for c in extra_categories)
                )
                for category in extra_categories:
                    self.__add_extra_category_if_not_exists(existing_point, category)
            else:
                self.__logger.debug('Point already exist: %s. No missing categories to append. Ignored')
            return group, None

        # Add point to group
        self.__logger.debug('New point created: %s', str(point))
        group.points.append(point)
        return group, point

    @staticmethod
    def __add_extra_category_if_not_exists(point: CartographyPoint, category: CartographyCategory):
        if category != point.category and category not in point.extra_categories:
            point.extra_categories.append(category)

    # Post-treatments
    def __treat_group_links(self, room: CartographyRoom):
        # TODO automatize from category description ?
        for column_base_group in [g for g in room.groups.values() if g.category == CartographyCategory.COLUMN_BASE]:
            category_number = column_base_group.category_number
            column_group = next(
                (g for g in room.groups.values()
                 if g.category == CartographyCategory.COLUMN and g.category_number == category_number),
                None)
            if column_group:
                self.__logger.debug('Column #%d found for base #%d', column_group.category_number, category_number)
                column_base_group.linked.append(column_group)
            else:
                self.__logger.warning('No column found for base #%d ', category_number)
