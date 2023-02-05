"""
Module for parser
"""

import logging
import os
from typing import Optional, Tuple

import utils
from model import CartographyCategory, CartographyGroup, CartographyPoint, CartographyRoom
from parsing import config as parse_config
from reading import CartographyFile, CartographyFilePoint
from utils.collection import dict as dict_utils
from . import utils as parse_utils
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
        point_with_groups_by_location = {}
        for file_point in file.points:
            context.row = file_point.row
            point, group = self.__parse_point(context, file_point)

            # Regroup point with group by location
            if group is not None:
                point_with_groups = utils.collection.dict.get_or_create(
                    point_with_groups_by_location,
                    str(point.location),
                    []
                )
                point_with_groups.append((point, group))

        # Create junctions
        filter(lambda items: len(items) > 1, point_with_groups_by_location.values())
        for point_with_groups in point_with_groups_by_location.values():
            parse_utils.junction.create_junctions(context, point_with_groups)
        self.__logger.debug('<%d> junctions created!', len(context.room.junctions))

        # Post-treatments
        self.__treat_group_links(context.room)

        return context.room

    def __parse_point(
            self,
            context: ParseContext,
            file_point: CartographyFilePoint
    ) -> Tuple[CartographyPoint, Optional[CartographyGroup]]:
        point = CartographyPoint()

        # Set properties
        point.name = file_point.point_name
        point.group_identifier = file_point.group_identifier
        point.location = file_point.location
        point.observations = file_point.observations.split(', ')

        # Determine category and interest type
        category_label = file_point.category
        point.category = parse_utils.category.parse_point_category(context, category_label)
        point.interest = parse_utils.interest.parse_point_interest(
            context,
            file_point.interest_type or '',
            required=parse_utils.category.require_interest(point.category)
        )

        # Determine group
        group_identifier = file_point.group_identifier
        group = parse_utils.group.get_or_create(context, point.category, category_label, group_identifier)

        # Determine additional categories and comments
        if group.category is not point.category:
            point.additional_categories.add(group.category)
            point.comments.append(parse_utils.group.build_group_name(category_label, group_identifier))
        else:
            point.comments.append(group.name)
        point.comments += point.observations

        self.__logger.debug('New point created: %s', str(point))

        # Add point to required group
        group.points.append(point)

        return point, group

    # Post-treatments
    def __treat_group_links(self, room: CartographyRoom):
        # TODO automatize from category description ?
        for group in [g for g in room.groups.values() if g.category == CartographyCategory.COLUMN_BASE]:
            group_name = group.name

            pattern = dict_utils.get_key(parse_config.category.by_pattern, CartographyCategory.COLUMN)
            match = utils.string.match_ignore_case('(' + pattern + '( [0-9]+)?)', group_name, False)
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
