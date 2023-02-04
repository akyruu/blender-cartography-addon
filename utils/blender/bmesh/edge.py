"""
Module for utility blender mesh methods
"""

from typing import Callable, List, Tuple

from bmesh.types import BMEdge, BMesh, BMVert

import utils
from utils.math import BiLocation, Location
from . import vert as vert_utils


# METHODS =====================================================================
def new(bm: BMesh, vert1: BMVert, vert2: BMVert) -> BMEdge:
    edge = get(bm, [vert1, vert2])  # FIXME test
    if edge:  # FIXME test
        return edge  # FIXME test
    return bm.edges.new([vert1, vert2])  # noqa


def get(bm: BMesh, vertices: List[BMVert] or Tuple[BMVert]) -> BMEdge:
    return bm.edges.get(vertices)  # noqa


def remove_all(bm: BMesh, edges: List[BMEdge]):
    for edge in edges:
        bm.edges.remove(edge)


def has_2d_junction(edge1: BMEdge or BiLocation, edge2: BMEdge or BiLocation) -> bool:
    return __has_junction(edge1, edge2, vert_utils.same_2d_position)


def has_3d_junction(edge1: BMEdge or BiLocation, edge2: BMEdge or BiLocation) -> bool:
    return __has_junction(edge1, edge2, vert_utils.same_3d_position)


def __has_junction(
        edge1: BMEdge or BiLocation,
        edge2: BMEdge or BiLocation,
        predicate: Callable[[BMVert or Location, BMVert or Location], bool]
) -> bool:
    vert1a, vert1b = __get_vertices(edge1)
    vert2a, vert2b = __get_vertices(edge2)
    return predicate(vert1a, vert2a) \
        or predicate(vert1a, vert2b) \
        or predicate(vert1b, vert2a) \
        or predicate(vert1b, vert2b)


def same_2d_position(edge1: BMEdge or BiLocation, edge2: BMEdge or BiLocation) -> bool:
    return _same_position(edge1, edge2, vert_utils.same_2d_position)


def same_3d_position(edge1: BMEdge or BiLocation, edge2: BMEdge or BiLocation) -> bool:
    return _same_position(edge1, edge2, vert_utils.same_3d_position)


def _same_position(
        edge1: BMEdge or BiLocation,
        edge2: BMEdge or BiLocation,
        predicate: Callable[[BMVert or Location, BMVert or Location], bool]
) -> bool:
    vert1a, vert1b = __get_vertices(edge1)
    vert2a, vert2b = __get_vertices(edge2)
    return (predicate(vert1a, vert2a) and predicate(vert1b, vert2b)) \
        or (predicate(vert1a, vert2b) and predicate(vert1b, vert2a))


def __get_vertices(edge: BMEdge or BiLocation) -> BiLocation:
    return edge.verts if isinstance(edge, BMEdge) else edge


def get_vertices(edges: List[BMEdge]) -> List[BMVert]:
    vertices = []
    for vert1, vert2 in [e.verts for e in edges]:
        vertices.append(vert1)
        vertices.append(vert2)
    return utils.collection.list.remove_duplicates(vertices)


def get_duplicated(edges: List[BMEdge]) -> List[Tuple[BMEdge, int]]:
    duplicated_edges = []
    visited_edges = []
    for edge in edges:
        if edge not in visited_edges:
            duplicated = [e for e in edges if same_3d_position(e, edge)]
            visited_edges += duplicated

            count = len(duplicated)
            if count > 1:
                duplicated_edges.append((edge, count))
    return duplicated_edges
