"""
Module for utility dictionary (Dict) methods
"""

from typing import Callable, Dict, List, Optional, Union

from utils.common import K, V
from . import list


# METHODS =====================================================================
def get_or_create(d: Dict[K, V], key: K, init: Union[V, Callable[[], V]]) -> V:
    value = d.get(key)
    if not value:
        value = init() if callable(init) else init
        d[key] = value
    return value


def get_key(d: Dict[K, V], value: V) -> Optional[K]:
    return list.inext(k for k, v in d.items() if v == value)


def pop_all(d: Dict[K, V], keys: List[K]):
    for key in keys:
        d.pop(key)
