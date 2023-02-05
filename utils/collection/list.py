"""
Module for utility list methods
"""

from typing import Callable, Dict, List, Optional, Tuple, Union

from utils.common import T, U, Predicate

# TYPES =======================================================================
DynamicIndex = Union[Predicate, Tuple[Predicate, int]]
StaticIndex = Union[int, Tuple[T, int], T]
GenericIndex = Union[DynamicIndex, StaticIndex]


# METHODS =====================================================================
def contains_one(lst: List[T], sub_lst: List[T]) -> bool:
    return next((e for e in sub_lst if e in lst), None) is not None


def contains_all(lst: List[T], sub_lst: List[T]) -> bool:
    return next((e for e in sub_lst if e not in lst), None) is None


def get_last(lst: List[T]) -> Optional[T]:
    """Get last item in list"""
    return lst[-1] if lst and len(lst) > 0 else None


def flat_map(f: Callable[[T], U], items: List[T]) -> List[U]:
    flat_items = []
    for item in items:
        flat_items.extend(f(item))
    return flat_items


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


# Mapping ---------------------------------------------------------------------
def group_values(lst: List[T], get_group_key: Callable[[T], U]) -> Dict[U, List[T]]:
    groups = {}
    for item in lst:
        key = get_group_key(item)
        items = groups.get(key)
        if items is None:
            items = []
            groups[key] = items
        items.append(item)
    return groups


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
        value = next((e for e in lst if dyn_index(e)), None)
        return lst.index(value) if value else dft
    return lst.index(dyn_index)
