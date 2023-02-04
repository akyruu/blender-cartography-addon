"""
Module for common elements
"""

from typing import Callable, TypeVar

# TYPES =======================================================================
T = TypeVar('T')
U = TypeVar('U')

K = TypeVar('K')
V = TypeVar('V')

Predicate = Callable[[T], bool]
