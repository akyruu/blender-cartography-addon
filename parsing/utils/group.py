"""
Module for treat groups
"""

import re
from typing import Optional

import config
import utils
from model import CartographyCategory, CartographyGroup, CartographyRoom
from parsing.model import ParseContext
from .category import is_outline


# METHODS =====================================================================
def find(context: ParseContext, partial_name: str, category: CartographyCategory, room: CartographyRoom) \
        -> Optional[CartographyGroup]:
    groups = [
        g for g in room.groups.values()
        if g.category == category and utils.string.match_ignore_case(partial_name, g.name, False)
    ]
    count = len(groups)
    if count > 1:
        context.logger.warning('Too much group found for name <%s>: current=<%d> expected=<%d>', partial_name, count, 1)
        return None
    return groups[0] if count == 1 else None


def get_or_create(
        context: ParseContext,
        category: CartographyCategory,
        group_name: Optional[str] = None,
        group_identifier: Optional[int] = None
) -> CartographyGroup:
    group_name, group_category = (build_group_name(CartographyCategory.OUTLINE.name), CartographyCategory.OUTLINE) \
        if is_outline(category) \
        else (build_group_name(group_name or category.name, group_identifier), category)

    group = context.room.groups.get(group_name, None)
    if not group:
        if is_outline(group_category):
            group = context.room.outline_group
        if not group:
            context.logger.debug('Create new group <%s>', group_name)
            group = CartographyGroup(group_name, group_category)
            context.room.groups[group_name] = group

            if is_outline(group_category):
                context.room.outline_group = group
    else:
        context.logger.debug('Use existing group <%s>', group_name)
    return group


def build_group_name(group_base_name: str, group_identifier: Optional[int] = None) -> str:
    return group_base_name.strip().capitalize() + (' ' + str(group_identifier) if group_identifier else '')


def match_category_in_observation(pattern: str, value: str) -> re.Match:
    m = utils.string.match_ignore_case(pattern, value, True)
    if not m:
        pattern = '(?!(' + '|'.join(config.mappings.words['proximity']) + ').)* ' + pattern
        m = utils.string.match_ignore_case(pattern, value, True)
        if not m:
            pattern += '.*'
            m = utils.string.match_ignore_case(pattern, value, True)
    return m
