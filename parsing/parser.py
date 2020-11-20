"""
Module for parser
"""

import logging
import os

from model import CartographyCategory, CartographyPoint, CartographyRoom
from reading import CartographyFile, CartographyFilePoint
from . import utils as parse_utils
from .exception import CartographyParserException
from .model import ParseContext


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

        # Post-treatments #
        # Junctions
        parse_utils.junction.determinate_junctions(self.__context)
        if len(self.__context.junctions) > 0:
            parse_utils.junction.update_groups_for_junctions(self.__context)

        return self.__context.room

    def __parse_point(self, file_point: CartographyFilePoint):
        categories = parse_utils.category.parse_categories(file_point.observations, True)
        for category, cat_match in categories:
            point = CartographyPoint()

            # Set properties
            observation = cat_match.group(0)
            point.name = file_point.point_name + ' (' + observation + ')'
            point.location = file_point.location
            point.observations = [observation]

            # Get or create group
            group = parse_utils.group.get_or_create_group(self.__context, point.observations)

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

            # Create and add point to current room
            self.__context.logger.debug('New point created: %s', str(point))
            group.points.append(point)
