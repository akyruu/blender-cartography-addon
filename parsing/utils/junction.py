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
def create_junctions(context: ParseContext, groups_points: List[Tuple[CartographyGroup, CartographyPoint]]):
    count = len(groups_points)
    for i in range(0, count):
        group1, point1 = groups_points[i]
        for j in range(i + 1, count):
            group2, point2 = groups_points[j]
            __logger.debug(
                'Add junction point between groups <%s> and <%s>: <%s>',
                group1.name, group2.name, point1.name
            )

            junction = context.room.get_junction(group1, group2)
            if not junction:
                junction = context.room.add_junction(group1, group2)
            junction.add_points(point1, point2)
