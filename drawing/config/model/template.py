"""
Configuration model for template
"""

from enum import Enum
from typing import Dict, NamedTuple, Union


class CartographyTemplateConfigItem(NamedTuple):
    name: str
    z_translation: Union[int, float]


class CartographyTemplateConfig(NamedTuple):
    name: str
    items_by_enum: Dict[Enum, CartographyTemplateConfigItem]
