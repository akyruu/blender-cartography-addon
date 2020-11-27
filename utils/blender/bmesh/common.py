"""
Module for utility blender mesh methods
"""

from typing import List, Union

from bmesh.types import BMEdge, BMFace, BMVert


# CLASSES =====================================================================
class Geometry:
    # Constructor -------------------------------------------------------------
    def __init__(self, _all: List[Union[BMVert, BMEdge, BMFace]] = None):
        self.all = _all or []
        self.vertices = [e for e in self.all if isinstance(e, BMVert)]
        self.edges = [e for e in self.all if isinstance(e, BMEdge)]
        self.faces = [e for e in self.all if isinstance(e, BMFace)]

    # Methods -----------------------------------------------------------------
    def append(self, element: Union[BMVert, BMEdge, BMFace]):
        self.all.append(element)
        self.__get_list(element).append(element)

    def append_all(self, elements: List[Union[BMVert, BMEdge, BMFace]]):
        for element in elements:
            self.append(element)

    def remove(self, element: Union[BMVert, BMEdge, BMFace]):
        self.all.remove(element)
        self.__get_list(element).remove(element)

    def __get_list(self, element: Union[BMVert, BMEdge, BMFace]) -> List[Union[BMVert, BMEdge, BMFace]]:
        if isinstance(element, BMVert):
            return self.vertices
        elif isinstance(element, BMEdge):
            return self.edges
        elif isinstance(element, BMFace):
            return self.faces
        raise Exception('Unexpected geometry type: <{}>. Expected: BMVert, BMEdge, BMFace', type(element))

    def clear(self):
        self.all.clear()
        self.vertices.clear()
        self.edges.clear()
        self.faces.clear()
