import os
from enum import Enum
from typing import Optional, List

import utils
from utils.object import TypeMapper


# TYPES =======================================================================
class ColumnModelCategory(Enum):
    """Category of column"""
    NORMAL = 1
    COORDINATE = 2


class ColumnModel:
    """Representation of column in table for patterns configuration"""
    name: str = ''
    header: str = ''
    pattern: str = ''
    ignore: bool = False
    category: ColumnModelCategory = ColumnModelCategory.NORMAL

    def __repr__(self):
        return self.__dict__.__repr__()


class TablePattern:
    """Representation of table for patterns configuration"""

    def __init__(self, headers: List[List[ColumnModel]] = None, columns: List[ColumnModel] = None):
        self.headers = headers or []
        self.columns = columns or []

    def include(self, *categories: List[ColumnModelCategory]):
        return TablePattern(
            [[h for h in hs if h.category in categories] for hs in self.headers if len(hs) > 0],
            [c for c in self.columns if c.category in categories]
        )

    def exclude(self, *categories: List[ColumnModelCategory]):
        return TablePattern(
            [[h for h in hs if h.category not in categories] for hs in self.headers if len(hs) > 0],
            [c for c in self.columns if c.category not in categories]
        )

    def __repr__(self):
        return self.__dict__.__repr__()


class TablePatternTypeMapper(TypeMapper):
    def map_type(self, path: str) -> Optional[type]:
        if utils.string.match_ignore_case('headers\\[\\d+]\\[\\d+]|columns\\[\\d+]', path):
            return ColumnModel
        elif path.endswith('.category'):
            return ColumnModelCategory
        return None

    def map_value(self, path: str, value: any) -> Optional[any]:
        if path.endswith('.category'):
            return ColumnModelCategory[value]


# CONFIG ======================================================================
# Excel pattern
excel = utils.object.to_class(
    utils.io.file.read_json(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), 'patterns_excel.json')
    ),
    TablePattern,
    TablePatternTypeMapper()
)
print('[Config] Patterns - Excel: {}', excel)
