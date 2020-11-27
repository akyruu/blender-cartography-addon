"""
Module for common elements
"""

from typing import Callable, TypeVar

# TYPES =======================================================================
T = TypeVar('T')

K = TypeVar('K')
V = TypeVar('V')

Predicate = Callable[[T], bool]
