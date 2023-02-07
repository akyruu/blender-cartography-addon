"""
Module for interest point drawer
"""

import logging
from typing import List

import bpy
import utils
from mathutils import Vector
from model import CartographyPoint, CartographyCategory, CartographyCategoryType, CartographyInterestType, \
    CartographyRoom
from utils.math import Location
from ..common import CartographyRoomDrawer, CartographyTemplate
from ...template.model import CartographyTemplateItem


# Classes =====================================================================
class CartographyInterestPointDrawer(CartographyRoomDrawer):
    """Drawer of interest points in room for cartography"""

    # Fields ------------------------------------------------------------------
    __logger = logging.getLogger('CartographyInterestPointDrawer')

    # Constructor -------------------------------------------------------------
    def __init__(self, template: CartographyTemplate):
        CartographyRoomDrawer.__init__(self, 'Interest Points', template)

    # Methods -----------------------------------------------------------------
    # Draw
    def draw(self, room: CartographyRoom, collection: bpy.types.Collection):
        interest_points = [p for p in room.all_points if p.category.type == CartographyCategoryType.INTEREST]
        points_by_category = utils.collection.list.group_values(interest_points, lambda p: p.category)

        for category, points in points_by_category.items():
            category_collection_name = category.name.replace('_', ' ').title()
            category_collection = utils.blender.collection.get_or_create(category_collection_name, collection)
            self.__draw_points(category, points, category_collection)

    def __draw_points(
            self,
            category: CartographyCategory,
            points: List[CartographyPoint],
            collection: bpy.types.Collection
    ):
        if category.options.structured:
            groups = utils.collection.list.group_values(points, lambda p: p.group_identifier)
            for group_identifier, group_points in groups.items():
                self.__draw_structured_points(category, group_identifier, group_points, collection)
        else:
            for point in points:
                self.__draw_interest_point(point, collection)

    def __draw_structured_points(
            self,
            category: CartographyCategory,
            group_identifier: int,
            points: List[CartographyPoint],
            collection: bpy.types.Collection
    ) -> bool:
        group_name = f'{collection.name} {group_identifier} (' + ', '.join([p.name for p in points]) + ')'
        self.__logger.debug(
            'Draw structured group: %s with points %s',
            group_name, str([p.name + ' (' + str(p.location) + ')' for p in points])
        )

        # Check if minimum number of points exists
        points_count = len(points)
        if points_count < 3:
            self.__logger.error(
                '[%s] Structured group required 3 points minimum, only %d available. Ignored',
                group_name, points_count
            )
            return False

        # Build mesh
        mesh_name = f'{category.name.lower()}_{group_identifier}_mesh'
        mesh = utils.blender.mesh.create(mesh_name)
        bm = utils.blender.mesh.edit(mesh)

        # Mesh - Create outline vertices
        origin = points[0].location
        vector = utils.math.diff_vector((0, 0, 0), origin)

        locations = [utils.math.translate(p.location, vector) for p in points]
        locations = list(filter(
            lambda loc: next(
                (l_ for l_ in locations if l_ != loc and utils.math.same_2d_position(l_, loc) and l_.z < loc.z),
                None
            ) is None,
            locations
        ))  # keep only the grounded point
        locations_count = len(locations)
        if locations_count < 3:
            self.__logger.debug(
                '[%s] Insufficient locations (%d < 3) after filter: %s. Ignored',
                group_name, locations_count, str(locations)
            )
            return False

        outline_vertices = [utils.blender.bmesh.vert.new(bm, loc) for loc in locations]
        self.__logger.debug('[%s] Outline vertices created: %s', group_name, str([v.co for v in outline_vertices]))

        # Mesh - Create outline edges
        outline_vertices_count = len(outline_vertices)
        # WARNING! Order must be respected for this step
        outline_edges = [
            utils.blender.bmesh.edge.new(bm, outline_vertices[i - 1], outline_vertices[i])
            for i in range(1, outline_vertices_count)
        ]

        # Close outline
        close_edge = utils.blender.bmesh.edge.new(bm, outline_vertices[0], outline_vertices[outline_vertices_count - 1])
        outline_edges.append(close_edge)

        self.__logger.debug(
            '[%s] Outline edges created: %s',
            group_name, str([[v.co for v in e.verts] for e in outline_edges])
        )

        # Mesh create faces and additional vertices/edges
        if category == CartographyCategory.BANK:
            # Add a centroid (at 3 meter of ground) # TODO use the max z for this proper
            centroid_location = utils.math.translate(utils.math.centroid([v.co for v in outline_vertices]), (0, 0, 3))
            centroid_vertex = utils.blender.bmesh.vert.new(bm, centroid_location)
            self.__logger.debug('[%s] Centroid vertex created: %s', group_name, str(centroid_vertex.co))

            # Create edges with all outline vertices and centroid vertex
            centroid_edges = [utils.blender.bmesh.edge.new(bm, centroid_vertex, v) for v in outline_vertices]
            self.__logger.debug(
                '[%s] Centroid edges created: %s',
                group_name, str([[v.co for v in e.verts] for e in centroid_edges])
            )

            # Create faces from centroid edges and outline edges
            faces = []
            for outline_edge in outline_edges:
                edges = [outline_edge]
                edges += [e for e in centroid_edges if utils.collection.list.contains_one(e.verts, outline_edge.verts)]
                faces += utils.blender.bmesh.face.new(bm, edges)
        else:
            # Mesh - Create plane from outline edges
            faces = utils.blender.bmesh.face.new(bm, outline_edges)

            # Build block
            utils.blender.bmesh.ops.extrude_z(bm, faces, 1.5)

        self.__logger.debug('Faces created: %s', str([[v.co for v in f.verts] for f in faces]))

        # Build and place object from updated mesh
        utils.blender.mesh.update(mesh, bm)
        utils.blender.object.create_from_mesh(group_name, origin, mesh, collection)

        return True

    def __draw_interest_point(self, point: CartographyPoint, collection: bpy.types.Collection):
        if point.category == CartographyCategory.ANTHROPOGENIC_OBJECT:
            drawn = self.__draw_anthropogenic_object(point, collection)
        else:
            drawn = self.__draw_other(point, collection)

        if not drawn:
            self.__draw_unknown(point, collection)

    def __draw_anthropogenic_object(self, point: CartographyPoint, collection: bpy.types.Collection) -> bool:
        self.__logger.debug('Draw anthropogenic object: <%s>', str(point))

        # Check point
        interest_type = point.interest
        if interest_type is None:  # FIXME move the unknown code ?
            self.__logger.warning('An interest is required for anthropic object point: <%s>.', str(point))
            return False
        template_item = self._get_template_interest_item(interest_type)

        # Get template
        if not template_item or not template_item.object:
            self.__logger.error('No template found for anthropogenic object: <%s>. Ignored', interest_type)
            return False

        # Create objects
        location = Vector((point.location.x, point.location.y, point.location.z))
        utils.blender.object.create_from_template(point.get_label(), location, template_item.object, collection)

        return True

    def __draw_other(self, point: CartographyPoint, collection: bpy.types.Collection) -> bool:
        self.__logger.debug('Draw other interest point: <%s>', point.name)
        self.__draw_obj(point, point.category, point.interest, collection)
        return True

    def __draw_unknown(self, point: CartographyPoint, collection: bpy.types.Collection):
        self.__logger.debug('Draw unknown point <%s> in collection <%s>)', point.name, collection.name)
        self.__draw_obj(point, CartographyCategory.UNKNOWN, CartographyInterestType.UNKNOWN, collection)

    def __draw_obj(
            self,
            point: CartographyPoint,
            category: CartographyCategory,
            interest: CartographyInterestType,
            collection: bpy.types.Collection
    ) -> bool:
        has_interest = interest is not None
        if has_interest:
            collection = utils.blender.collection.create(point.get_label(), collection)

        # Create base object
        base_name = f'{point.get_label()}_base' if has_interest else point.get_label()
        base_location = point.location
        base_template_item = self._get_template_category_item(category)
        base_obj_item = self.__draw_obj_item(base_name, base_location, base_template_item, collection)

        if interest:
            # Create interest image and place it on top of base object
            image_location = utils.math.translate(base_location, (0, 0, base_obj_item.dimensions.z))
            image_template_item = self._get_template_interest_item(interest)
            self.__draw_obj_item(f'{point.get_label()}_icon', image_location, image_template_item, collection)
        return True

    @staticmethod
    def __draw_obj_item(
            obj_name: str,
            location: Location,
            template_item: CartographyTemplateItem,
            collection: bpy.types.Collection
    ) -> bpy.types.Object:
        # Check template
        if not template_item or not template_item.object:
            return None

        # Create object
        obj_location = utils.math.translate(location, (0, 0, template_item.config.z_translation))
        return utils.blender.object.create_from_template(obj_name, obj_location, template_item.object, collection)
