import logging

import action
import utils

# VARIABLES ===================================================================
__name = 'main'
__logger = logging.getLogger(__name)
__actions = [
    action.calculate_coordinates,
    action.generate_blender_file
]

# ARGUMENTS ===================================================================
utils.args.add('-a', '--action', str, 'Launch a main action directly')
utils.args.add('-f', '--file', str, 'File with coordinates')
utils.args.add('-o', '--output', str, 'Name of file to write')
args = utils.args.parse()


# METHODS =====================================================================
def entry_point(action_name: str):
    """Entry point for execute an action"""
    __logger.info('Launch action <%s>...', action_name)
    action_inst = utils.collection.list.pnext(__actions, lambda a: a.name == action_name)
    if action_inst:
        action_inst.entry_point(args)
    else:
        raise Exception('Unknown action: <{}>'.format(action))
