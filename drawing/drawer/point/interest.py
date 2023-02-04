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
from ..common import CartographyRoomDrawer, CartographyTemplate


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
        group_name = '{} {} ({})'.format(collection.name, group_identifier, ', '.join([p.name for p in points]))
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
        mesh_name = '{}_{}_mesh'.format(category.name.lower(), group_identifier)
        mesh = utils.blender.mesh.create(mesh_name)
        bm = utils.blender.mesh.edit(mesh)

        # Mesh - Create outline vertices
        origin = points[0].location
        vector = utils.math.diff_vector((0, 0, 0), origin)

        locations = [utils.math.translate(p.location, vector) for p in points]
        locations = list(filter(
            lambda loc: utils.collection.list.pnext(
                locations,
                lambda l: l != loc and utils.math.same_2d_position(l, loc) and l.z < loc.z,
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
            # Add a centroid (at 1.5 meter of ground) # TODO use the max z for this proper
            centroid_location = utils.math.translate(utils.math.centroid([v.co for v in outline_vertices]), (0, 0, 1.5))
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
        if point.interest is None:  # FIXME move the unknown code ?
            self.__logger.warning('An interest is required for anthropic object point: <%s>.', str(point))
            return False
        else:
            interest = point.interest
            template = self._get_template_object(interest, 'interest type')

        # Get template
        if template is None:
            self.__logger.error('No template found for anthropogenic object: <%s>. Ignored', point.interest)
            return False

        # Create objects
        location = Vector((point.location.x, point.location.y, point.location.z))
        utils.blender.object.create_from_template(point.get_label(), location, template, collection)

        return True

    def __draw_other(self, point: CartographyPoint, collection: bpy.types.Collection) -> bool:
        self.__logger.debug('Draw interest point: <%s>', str(point))

        # Get template and create point
        template = self._get_template_object(point.category, 'category')
        if template is None:
            self.__logger.warning('No template found for interest point: <%s>.', str(point))
            return False
        obj = utils.blender.object.create_from_template(point.get_label(), point.location, template, collection)

        # Icon
        if point.interest is not None:
            interest = point.interest

            # Get icon template
            template = self._get_template_object(interest, 'interest type')
            if template is None:
                self.__logger.warning('No template found for interest type: <%s>.', str(interest))
                return False

            # Create image
            name = obj.name + '_icon'
            z = obj.location.z + obj.dimensions.z  # noqa
            utils.blender.object.create_from_template(name, (obj.location[0], obj.location[1], z), template, collection)
        return True

    def __draw_unknown(self, point: CartographyPoint, collection: bpy.types.Collection):
        self.__logger.debug('Draw unknown point', point, collection)

        # FIXME determined model with icon with config ?
        base_template = self._get_template_object(CartographyCategory.UNKNOWN, 'category')
        base_obj_name = point.name + ' (' + ', '.join(point.observations) + ')'
        obj = utils.blender.object.create_from_template(base_obj_name, point.location, base_template, collection)

        # Create image
        icon_template = self._get_template_object(CartographyInterestType.UNKNOWN, 'interest type')
        icon_obj_name = base_obj_name + '_icon'
        z = obj.location.z + obj.dimensions.z  # noqa
        utils.blender.object.create_from_template(icon_obj_name, (obj.location[0], obj.location[1], z), icon_template,
                                                  collection)
