"""
Module for parser
"""

import logging
import os
from typing import Optional, Tuple

import mappings
import utils
from model import CartographyCategory, CartographyGroup, CartographyPoint, CartographyRoom
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
        point_with_groups_by_location = {}
        for file_point in file.points:
            self.__context.row = file_point.row
            point, group = self.__parse_point(file_point)

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
            parse_utils.junction.create_junctions(self.__context, point_with_groups)
        self.__logger.debug('<%d> junctions created!', len(self.__context.room.junctions))

        # Post-treatments
        self.__treat_group_links(self.__context.room)

        # PT - Junctions @deprecated
        # FIXME useless ? parse_utils.junction_old.determinate_junctions(self.__context)
        # FIXME useless ? if len(self.__context.junctions) > 0:
        # FIXME useless ?     parse_utils.junction_old.update_groups_for_junctions(self.__context)

        return self.__context.room

    def __parse_point(self, file_point: CartographyFilePoint) -> Tuple[CartographyPoint, Optional[CartographyGroup]]:
        point = CartographyPoint()

        # Set properties
        point.name = file_point.point_name
        point.location = file_point.location
        point.observations = file_point.observations

        # Determine category and interest type
        category_label = file_point.category
        point.category = parse_utils.category.parse_point_category_v1p2(self.__context, category_label)
        point.interest = parse_utils.interest.parse_point_interest_v1p2(
            self.__context,
            file_point.interest_type,
            required=parse_utils.category.require_interest(point.category)
        )

        # Determine group
        group_identifier = file_point.group_identifier
        group = parse_utils.group.get_or_create(self.__context, point.category, category_label, group_identifier)

        # Determine additional categories and comments
        if group.category is not point.category:
            point.additional_categories.add(group.category)
            point.comments.append(parse_utils.group.build_group_name(category_label, group_identifier))
        else:
            point.comments.append(group.name)
        point.comments += point.observations

        self.__context.logger.debug('New point created: %s', str(point))

        # Add point to required group
        group.points.append(point)

        return point, group

    # Post-treatments
    def __treat_group_links(self, room: CartographyRoom):
        # TODO automatize from category description ?
        for group in [g for g in room.groups.values() if g.category == CartographyCategory.COLUMN_BASE]:
            group_name = group.name

            pattern = dict_utils.get_key(mappings.cartography_point_category, CartographyCategory.COLUMN)
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
