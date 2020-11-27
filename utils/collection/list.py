"""
Module for utility list methods
"""

from typing import Callable, Iterator, List, Optional, Tuple, Union

from utils.common import T, Predicate

# TYPES =======================================================================
DynamicIndex = Union[Predicate, Tuple[Predicate, int]]
StaticIndex = Union[int, Tuple[T, int], T]
GenericIndex = Union[DynamicIndex, StaticIndex]


# METHODS =====================================================================
def contains_all(lst: List[T], sub_lst: List[T]) -> bool:
    return inext(e for e in sub_lst if e not in lst) is None


def get_last(lst: List[T]) -> Optional[T]:
    """Get last item in list"""
    return lst[-1] if lst and len(lst) > 0 else None


def inext(iterator: Iterator[T], dft_value: Optional[T] = None) -> Optional[T]:  # noqa
    try:
        return next(iterator)
    except StopIteration:
        return dft_value


def pnext(lst: List[T], predicate: Predicate, dft_value: Optional[T] = None) -> Optional[T]:  # noqa
    return inext((e for e in lst if predicate(e)), dft_value)


# Extraction ------------------------------------------------------------------
def sublist(lst: List[T], start: StaticIndex, end: Optional[StaticIndex] = None) -> List[T]:
    return lst[__start_index(lst, start):__end_index(lst, end)]


# Finding
def find_sublist(lst: List[T], start: DynamicIndex, end: Optional[DynamicIndex] = None) -> List[T]:
    return lst[__start_index(lst, start):__end_index(lst, end)]


# Insertion -------------------------------------------------------------------
def insert_values(lst: List[T], start: int, values: List[T]):
    i = start
    for e in values:
        lst.insert(i, e)
        i += 1


# Removing --------------------------------------------------------------------
def remove_values(lst: List[T], values: List[T]):
    for value in values:
        lst.remove(value)


def remove_sublist(lst: List[T], start: StaticIndex, end: Optional[StaticIndex] = None):
    start_index = __start_index(lst, start)
    for i in range(start_index, __end_index(lst, end)):
        lst.pop(start_index)


def remove_duplicates(lst: List[T]) -> List[T]:
    return list(dict.fromkeys(lst))


# METHODS - INTERNAL ==========================================================
def __start_index(lst: List[T], start: GenericIndex) -> int:
    return max(__determine_index(lst, start, 0), 0)


def __end_index(lst: List[T], end: Optional[GenericIndex]) -> int:
    return min(__determine_index(lst, end, len(lst)), len(lst))


def __determine_index(lst: List[T], dyn_index: Optional[GenericIndex], dft: int):
    if not dyn_index:
        return dft
    elif isinstance(dyn_index, int):
        return dyn_index
    elif isinstance(dyn_index, Tuple):
        dyn_index, added = dyn_index
        return __determine_index(lst, dyn_index, dft) + added
    elif isinstance(dyn_index, Callable):
        return lst.index(inext(e for e in lst if dyn_index(e)))
    return lst.index(dyn_index)
