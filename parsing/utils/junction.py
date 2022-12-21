"""
Module for treat junctions
"""

import logging
from typing import List, Tuple

from model import CartographyGroup, CartographyPoint
from ..model import ParseContext

# VARIABLES ===================================================================
__logger = logging.getLogger('parsing_utils_junction')


# METHODS =====================================================================
def create_junctions(context: ParseContext, point_with_groups: List[Tuple[CartographyPoint, CartographyGroup]]):
    count = len(point_with_groups)
    for i in range(0, count):
        point1, group1 = point_with_groups[i]
        for j in range(i + 1, count):
            point2, group2 = point_with_groups[j]
            __logger.debug(
                'Add junction point between groups <%s> and <%s>: <%s> (<%s>)',
                group1.name, group2.name, point1.name, point2.name
            )
            point1.additional_categories.update(point2.get_all_categories())  # FIXME temp fix for keep drawer 1.2
            point2.additional_categories.update(point1.get_all_categories())  # FIXME temp fix for keep drawer 1.2

            junction = context.room.get_junction(group1, group2)
            if not junction:
                junction = context.room.add_junction(group1, group2)
            junction.add_points(point1, point2)
