"""
Module for utility methods

History:
2020/08/21: v0.0.1
    + add utility methods for bmesh/mesh conversion
    + add utility methods for matching
"""

import math
import os
import re
import sys
from typing import Callable, Dict, Iterator, List, Optional, Tuple, TypeVar, Union

import bmesh
import bpy
from mathutils import Vector

# TYPES =======================================================================
T = TypeVar('T')

K = TypeVar('K')
V = TypeVar('V')


# METHODS =====================================================================
# Blender - Meshing -----------------------------------------------------------
def bmvert_global_coordinate(vert: bmesh.types.BMVert, obj: bpy.types.Object) -> Vector:
    """Get global coordinate for a vertex"""
    return obj.matrix_world @ vert.co  # noqa


def bmesh_extrude(
        bm: bmesh.types.BMesh,
        geom: List[Union[bmesh.types.BMVert, bmesh.types.BMEdge, bmesh.types.BMFace]]
) -> List[Union[bmesh.types.BMVert, bmesh.types.BMEdge, bmesh.types.BMFace]]:
    """Extrude a geometry and return vertices, edges and faces created"""
    prev_faces = [f for f in bm.faces]
    extruded = bmesh.ops.extrude_face_region(bm, geom=geom)
    extruded_geom = extruded['geom']

    # FIXME Add missing faces created in extruded geom for some reason
    if len(bm.faces) > len(prev_faces):
        extruded_geom += [f for f in bm.faces if f not in prev_faces]

    return extruded_geom


def bmesh_from_mesh(mesh: bpy.types.Mesh) -> bmesh.types.BMesh:
    """Create BMesh from Mesh"""
    if mesh.is_editmode:
        bm = bmesh.from_edit_mesh(mesh)
    else:
        bm = bmesh.new()
        bm.from_mesh(mesh)
    return bm


def bmesh_to_mesh(bm: bmesh.types.BMesh, mesh: bpy.types.Mesh):
    """Update Mesh with BMesh"""
    if bm.is_wrapped:
        bmesh.update_edit_mesh(mesh, False, False)
    else:
        bm.to_mesh(mesh)
        mesh.update()


def obj_get_mesh(obj: bpy.types.Object) -> bpy.types.Mesh:
    return obj.data  # noqa


# Dict ------------------------------------------------------------------------
def dict_get_or_create(d: Dict[K, V], key: K, init: Union[V, Callable[[], V]]) -> V:
    value = d.get(key)
    if not value:
        value = init() if callable(init) else init
        d[key] = value
    return value


# List ------------------------------------------------------------------------
def list_get_last(lst: List[T]) -> Optional[T]:
    """Get last item in list"""
    return lst[-1] if lst and len(lst) > 0 else None


def list_next(iterator: Iterator[T], dft_value: Optional[T] = None) -> Optional[T]:
    try:
        return next(iterator)
    except StopIteration:
        return dft_value


def list_reverse(lst: List[T]) -> List[T]:
    lst.reverse()
    return lst


def list_sublist(
        lst: List[T],
        start: Union[int, Tuple[T, int], T],
        end: Union[int, Tuple[T, int], T, None] = None
) -> List[T]:
    start_index = max(__list_sublist_index(lst, start, 0), 0)
    end_index = min(__list_sublist_index(lst, end, len(lst)), len(lst))
    return lst[start_index:end_index]


def __list_sublist_index(lst: List[T], idx: Union[int, Tuple[T, int], T, None], dft: int):
    if not idx:
        return dft
    elif isinstance(idx, int):
        return idx
    elif isinstance(idx, Tuple):
        return lst.index(idx[0]) + idx[1]
    return lst.index(idx)


# Math ------------------------------------------------------------------------
def math_3d_distance(p1: Vector, p2: Vector) -> float:
    return math.sqrt(
        math.pow(abs(p1.x - p2.x), 2)
        + math.pow(abs(p1.y - p2.y), 2)
        + math.pow(abs(p1.z - p2.z), 2)
    )


# Path ------------------------------------------------------------------------
def path_workspace() -> os.path:
    # FIXME ok for debug only
    paths = [path for path in sys.path if os.path.basename(path) == 'blender-cartography-addon']
    return paths[0]


# String - Match --------------------------------------------------------------
def match_ignore_case(pattern: str, value: str, exact: bool = True) -> re.Match:
    flags = re.IGNORECASE

    m = re.match(pattern, value, flags)
    if m is None and not exact:
        m = re.match(pattern + '.*', value, flags)
        if m is None:
            m = re.match('.*' + pattern + '.*', value, flags)
    return m
