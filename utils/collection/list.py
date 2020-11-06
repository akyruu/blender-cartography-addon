"""
Module for utility list (List) methods
"""

from typing import Iterator, List, Optional, Tuple, Union

from utils.common import T


# METHODS =====================================================================
def get_last(lst: List[T]) -> Optional[T]:
    """Get last item in list"""
    return lst[-1] if lst and len(lst) > 0 else None


def inext(iterator: Iterator[T], dft_value: Optional[T] = None) -> Optional[T]:
    try:
        return next(iterator)
    except StopIteration:
        return dft_value


def reverse(lst: List[T]) -> List[T]:
    lst.reverse()
    return lst


def sublist(
        lst: List[T],
        start: Union[int, Tuple[T, int], T],
        end: Union[int, Tuple[T, int], T, None] = None
) -> List[T]:
    start_index = max(__sublist_index(lst, start, 0), 0)
    end_index = min(__sublist_index(lst, end, len(lst)), len(lst))
    return lst[start_index:end_index]


def __sublist_index(lst: List[T], idx: Union[int, Tuple[T, int], T, None], dft: int):
    if not idx:
        return dft
    elif isinstance(idx, int):
        return idx
    elif isinstance(idx, Tuple):
        return lst.index(idx[0]) + idx[1]
    return lst.index(idx)
