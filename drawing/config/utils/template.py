"""
Mappings for drawing
"""

from enum import Enum
from typing import Dict, Union

from ..model.template import CartographyTemplateConfig, CartographyTemplateConfigItem


# INTERNAL ====================================================================
def item(name: str, z_translation: int or float) -> CartographyTemplateConfigItem:
    return CartographyTemplateConfigItem(name, z_translation)


def config(name: str, dct: Dict[Enum, Union[str, CartographyTemplateConfigItem]]) -> CartographyTemplateConfig:
    items_by_enum = {}
    for k, v in dct.items():
        items_by_enum[k] = v if isinstance(v, CartographyTemplateConfigItem) else item(v, 0)
    return CartographyTemplateConfig(name, items_by_enum)
