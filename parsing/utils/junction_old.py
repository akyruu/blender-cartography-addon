"""
Module for treat junctions

FIXME deprecated (useless with new way)
@deprecated
"""

import mappings
import utils
from model import CartographyGroup, CartographyPoint
from parsing.exception import CartographyParserException
from . import common, category as category_utils, group as group_utils
from ..model import JunctionGroup, ParseContext, PointGroupTuple


# METHODS =====================================================================
def determinate_junctions(context: ParseContext):
    for group in context.room.groups.values():
        for point in group.points:
            __determinate_junction(context, point, group)


def __determinate_junction(context: ParseContext, ext_point: CartographyPoint, ext_group: CartographyGroup):
    # Search observation sentence
    match = None
    for observation in ext_point.observations:
        m = utils.string.match_ignore_case(mappings.cartography_junction_pattern, observation, False)
        if m:
            match = m
            break
    if not match:
        return

    # Determinate point attributes to search
    partial_name = match.group(2)  # 1: junction word, 2: category (with optional number)
    category, cat_match = category_utils.parse_point_category(context, partial_name)

    # Search group
    int_group = group_utils.find(context, partial_name, category, context.room)
    if not int_group:
        context.logger.warning('Junction group <%s> not found for point <%s>', partial_name, ext_point.name)
        return

    # Set junction start/end in group
    junction_group = utils.collection.dict.get_or_create(
        context.junctions, int_group.name,
        lambda: JunctionGroup(context.room, int_group)
    )
    if junction_group.start is None:
        context.logger.debug('Junction group <%s>, start point found: %s', int_group.name, ext_point.name)
        junction_group.start = PointGroupTuple(ext_point, ext_group)
    elif junction_group.end is None:
        context.logger.debug('Junction group <%s>, end point found: %s', int_group.name, ext_point.name)
        junction_group.end = PointGroupTuple(ext_point, ext_group)
    else:
        raise CartographyParserException(context.row, ext_group.name, 'junction', '2 junctions: start and end')


def update_groups_for_junctions(context: ParseContext):
    for junction in context.junctions.values():
        __check_junction(context, junction)
        __update_groups_for_junction(context, junction)


def __check_junction(context: ParseContext, junction: JunctionGroup):
    if junction.end is None:
        context.logger.warning('No end found for junction group <%s>. Use the start point', junction.group.name)
        junction.end = junction.start
        # raise CartographyParserException(context.row, junction.group.name, 'junction', '2 junctions: start and end')
    elif junction.start.point == junction.end.point:
        raise CartographyParserException(
            context.row,
            '{}.points=[start=end={}]'.format(junction.group.name, junction.start.point.name),
            'junction',
            'Start point different of end point'
        )
    elif junction.start.group != junction.end.group:
        raise Exception('##TODO## start/end junction group is different')  # TODO
    elif not junction.start.group.category.outline:
        raise Exception('##TODO## junction group with another of outline')  # TODO


def __update_groups_for_junction(context: ParseContext, junction: JunctionGroup):
    # Update groups
    int_group = junction.group
    int_points = int_group.points
    ext_group = junction.start.group
    ext_points = ext_group.points

    context.logger.debug('Update groups for junction group <%s>...', int_group.name)
    try:
        # Split external points
        fst_ext_points: list = utils.collection.list.sublist(ext_points, 0, junction.start.point)
        mid_ext_points: list = utils.collection.list.sublist(ext_points, junction.start.point,
                                                             (junction.end.point, 1))
        lst_ext_points: list = utils.collection.list.sublist(ext_group.points, (junction.end.point, 1))

        # Update external points
        ext_points.clear()
        ext_points += fst_ext_points

        ext_to_add_points = [junction.start.point] + int_points + [junction.end.point]
        ext_z = fst_ext_points[-2].location.z if len(fst_ext_points) > 1 \
            else (lst_ext_points[1].location.z if len(lst_ext_points) > 1
                  else None)
        if ext_z is not None and int_points[0].location.z != ext_z:
            ext_to_add_points = [common.normalize_z_axis(p, ext_z) for p in ext_to_add_points]
        ext_points += ext_to_add_points

        ext_points += lst_ext_points
        context.logger.debug(
            '<%d> points transferred from group <%s> to <%s>',
            len(int_points), int_group.name, ext_group.name
        )

        # Update internal points
        mid_ext_points.reverse()  # Reverse for keep order in new group
        int_points += mid_ext_points
        context.logger.debug(
            '<%d> points transferred from group <%s> to <%s>',
            len(mid_ext_points), ext_group.name, int_group.name)
    except ValueError as err:
        context.logger.error('Failed to update groups for junction group <%s>', int_group.name, exc_info=err)
