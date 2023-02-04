"""
Module for treat groups
"""

from typing import Optional

from model import CartographyCategory, CartographyGroup
from parsing.model import ParseContext
from .category import is_outline


# METHODS =====================================================================
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
