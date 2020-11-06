"""
Module for utility dictionary (Dict) methods
"""

from typing import Callable, Dict, Union

from utils.common import K, V


# METHODS =====================================================================
def get_or_create(d: Dict[K, V], key: K, init: Union[V, Callable[[], V]]) -> V:
    value = d.get(key)
    if not value:
        value = init() if callable(init) else init
        d[key] = value
    return value
