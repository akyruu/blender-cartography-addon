"""
Module for utility object methods
"""


# METHODS =====================================================================
def to_str(obj: any) -> str:
    return str(vars(obj))


def to_repr(obj: any) -> str:
    return obj.__class__.__name__ + '@' + to_str(obj)
