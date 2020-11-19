import argparse
import logging
import os

import bpy

import action
import utils

# VARIABLES ===================================================================
__logger = logging.getLogger('main')

# ARGUMENTS ===================================================================
arg_parser = argparse.ArgumentParser()

# Common
arg_parser.add_argument(
    '-a', '--action',
    type=str,
    help='Launch a main action directly'
)
arg_parser.add_argument(
    '-f', '--file',
    type=str,
    help='File with coordinates, required for certain actions'
)

# Calculate coordinates
arg_parser.add_argument(
    '-o', '--output',
    type=str,
    help='Name of file to write'
)

# Generate blender file
arg_parser.add_argument(
    '-e', '--export',
    type=str,
    help='Blend file to export created room'
)

args, unknown = arg_parser.parse_known_args(utils.blender.system.get_script_args())


# METHODS =====================================================================
def entry_point(action_name: str):
    """Entry point for execute an action"""
    __logger.info('Launch action <%s>...', action_name)
    if action_name == 'generate_blender_file':
        clear_scene()
        file = args.file
        if not file:
            raise Exception('A file required for action <{}>'.format(action))
        action.generate_blender_file(file)
        if args.export:
            export_blender_file(args.export)
    elif action_name == 'calculate_coordinates':
        file = args.file
        if not file:
            raise Exception('A file required for action <{}>'.format(action))

        target_path = args.output if args.output else file
        action.calculate_coordinates(file, target_path)
    else:
        raise Exception('Unknown action: <{}>'.format(action))


def clear_scene():
    bpy.ops.object.delete({'selected_objects': [bpy.context.scene.objects['Cube']]})


def export_blender_file(filepath: os.path):
    if os.path.exists(filepath):
        os.remove(filepath)
    bpy.ops.wm.save_as_mainfile(filepath=filepath)
