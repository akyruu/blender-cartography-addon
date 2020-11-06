"""
Module for parser
"""

import logging
import os

from model import CartographyPoint, CartographyRoom
from reading import CartographyFile, CartographyFilePoint
from . import __utils as parse_utils
from .__model import ParseContext


# CLASSES =====================================================================
class CartographyParser:
    """Cartography file parser"""

    # Fields ------------------------------------------------------------------
    __logger: logging.Logger = logging.getLogger('CartographyParser')

    # Constructor -------------------------------------------------------------
    def __init__(self):
        self.__context = ParseContext(self.__logger)

    # Methods -----------------------------------------------------------------
    # Reading
    def parse(self, file: CartographyFile):
        filename, extension = os.path.splitext(os.path.basename(file.path))
        self.__context.room = CartographyRoom(filename)
        self.__context.row = 0
        self.__context.junctions = {}

        # Read all point lines in file
        for line in file.points:
            self.__context.row = line.row
            self.__parse_point(line)

        # Post-treatment - Junctions
        parse_utils.junction.determinate_junctions(self.__context)
        if len(self.__context.junctions) > 0:
            parse_utils.junction.update_groups_for_junctions(self.__context)

        return self.__context.room

    def __parse_point(self, file_point: CartographyFilePoint):
        point = CartographyPoint()

        # Determine name and observations
        point.name = file_point.point_name
        if file_point.observations:
            point.name += ' (' + ', '.join(file_point.observations) + ')'
            point.observations = file_point.observations.copy()

        # Set location
        point.location = file_point.location

        # Get or create group
        group = parse_utils.group.get_or_create_group(self.__context, file_point)

        # Determine category and interest type
        category = group.category
        if file_point.observations:
            observations = ', '.join(file_point.observations)
            point.interest = parse_utils.common.check_interest(self.__context, observations)
            if point.interest is None:
                category, cat_match = parse_utils.category.parse_point_category(
                    self.__context,
                    observations,
                    point.category,
                    [group.category]
                )
        elif category is None:  # Always false in prod runtime
            raise Exception('Point line found but not the point type: #' + str(self.__context.row))
        point.category = category

        # Create and add point to current room
        self.__context.logger.debug('New point created: %s', str(point))
        group.points.append(point)
