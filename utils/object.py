"""
Module for utility object methods
"""
from typing import Optional, Type

from .common import T

# VARIABLES ===================================================================
__SEQUENCE_TYPES = (tuple, list, set, frozenset)


# TYPES =======================================================================
class TypeMapper:
    """Mapper of type for to_class method"""

    def map_type(self, path: str) -> Optional[type]:
        return None

    def map_value(self, path: str, value: any) -> Optional[any]:
        return None

    def map_obj_child(self, path: str) -> bool:
        return True


# METHODS =====================================================================
def to_str(obj: any) -> str:
    return str(vars(obj))


def to_repr(obj: any) -> str:
    return obj.__class__.__name__ + '@' + to_str(obj)


def to_class(obj: any, target_type: Type[T], type_mapper: TypeMapper = TypeMapper()) -> T:
    return __to_class(obj, target_type, type_mapper, '')


def __to_class(obj: any, target_type: Type[T], type_mapper: TypeMapper, path: str) -> T:
    if not isinstance(obj, dict):
        raise Exception('Object instance must be an dict')

    # Map target
    target_type = type_mapper.map_type(path) or target_type
    target = target_type()

    # Map item
    if type_mapper.map_obj_child(path):
        for name, value in obj.items():
            if not hasattr(target, name):
                raise Exception(f'Unknown attribute <{name}> for class <{target.__class__.__name__}>')

            attr_path = (path + '.' if path else '') + name
            attr_value = getattr(target, name)
            attr_type = type(attr_value)
            if isinstance(value, dict):
                if not isinstance(attr_value, dict):
                    value = __to_class(obj, attr_type, type_mapper, attr_path)
            elif isinstance(value, __SEQUENCE_TYPES) and isinstance(attr_value, __SEQUENCE_TYPES):
                value = __to_class_seq(value, type_mapper, attr_path)
            else:
                mapped_value = type_mapper.map_value(attr_path, value)
                if mapped_value:
                    value = mapped_value

            setattr(target, name, value)

    return target


def __to_class_seq(lst: list, type_mapper: TypeMapper, path: str) -> T:
    return type(lst)(
        __to_class(item, dict, type_mapper, f'{path}[{index}]') if isinstance(item, dict)
        else (
            __to_class_seq(item, type_mapper, f'{path}[{index}]')
            if isinstance(item, __SEQUENCE_TYPES)
            else item) for index, item in enumerate(lst)
    )
