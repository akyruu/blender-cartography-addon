"""
Module for plane drawer
"""

import logging
from typing import Dict, List, Optional

import bmesh
import bpy

from model import CartographyGroup
from templating import CartographyTemplate


# Classes =====================================================================
class CartographyPlaneContext:
    """Context of plane drawer"""

    # Constructor -------------------------------------------------------------
    def __init__(self, template: CartographyTemplate, logger: logging.Logger):
        self.template = template
        self.logger = logger

        self.mesh: Optional[bpy.types.Mesh] = None
        self.mat_wall_index = None
        self.mat_climbing_index = None
        self.bmesh: Optional[bmesh.types.BMesh] = None

        self.vertices_by_group: Dict[CartographyGroup, List[bmesh.types.BMVert]] = {}
        self.gate_vertices: List[bmesh.types.BMVert] = []
        self.outline_vertices: List[bmesh.types.BMVert] = []

        self.edges_by_group: Dict[CartographyGroup, List[bmesh.types.BMEdge]] = {}
        self.edges_by_z: Dict[float, List[bmesh.types.BMEdge]] = {}
        self.gate_edges: List[bmesh.types.BMEdge] = []
        self.outline_edges: List[bmesh.types.BMEdge] = []
