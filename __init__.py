import importlib
import logging.config
import os
import sys

import bpy

# BLENDER INFORMATION =========================================================
bl_info = {
    'name': '[ΩP] Cartography addon',
    'author': 'Akyruu',
    'version': (0, 0, 1),
    'blender': (2, 83, 0),
    'location': 'File > Import > Cartography (.csv, .tsv)',
    'description': 'Import CSV file with locations from Cartographie',
    'warning': '',
    'wiki_url': '',
    'tracker_url': '',
    'category': 'Import-Export'
}

# MODULES =====================================================================
modulesNames = [
    # Configuration
    'bca_config',
    # Model
    'bca_types',
    # Tools
    'bca_utils',
    # Service
    'mappings',  # Config
    'reading',
    'templating',
    'drawing',
    # View
    'gui',
]

# Importation --------------------------------------------------------------
modulesFullNames = [('{}'.format(moduleName)
                     if 'DEBUG_MODE' in sys.argv
                     else '{}.{}'.format(__name__, moduleName))
                    for moduleName in modulesNames]
for moduleFullName in modulesFullNames:
    if moduleFullName in sys.modules:
        importlib.reload(sys.modules[moduleFullName])
    else:
        globals()[moduleFullName] = importlib.import_module(moduleFullName)
        setattr(globals()[moduleFullName], 'modulesNames', modulesFullNames)


def modules() -> list:
    return [sys.modules[moduleName] for moduleName in modulesFullNames if moduleName in sys.modules]


# [Un]Register ----------------------------------------------------------------
def register():
    for module in modules():
        if hasattr(module, '__classes__'):
            for cls in module.__classes__:
                try:
                    bpy.utils.register_class(cls)
                except RuntimeError as err:
                    raise RuntimeError('Failed to register {0}. Cause: {1}'.format(cls, err))
        if hasattr(module, 'register'):
            module.register()


def unregister():
    for module in modules():
        if hasattr(module, 'unregister'):
            module.unregister()
        if hasattr(module, '__classes__'):
            for cls in reversed(module.__classes__):
                try:
                    bpy.utils.unregister_class(cls)
                except RuntimeError as err:
                    raise RuntimeError('Failed to unregister {0}. Cause: {1}'.format(cls, err))


# Debug -----------------------------------------------------------------------
def debug():
    for module in modules():
        if hasattr(module, 'debug'):
            module.debug()


# FIXME already exists in bca_utils.py
def workspace() -> os.path:
    # FIXME ok for debug only
    paths = [path for path in sys.path if os.path.basename(path) == 'blender-cartography-addon']
    return paths[0]


# ENTRY POINT =================================================================
if __name__ == "__main__":
    work_path = workspace()
    print(work_path)
    logging.config.fileConfig(
        fname=os.path.join(work_path, 'logging.conf'),
        disable_existing_loggers=False
    )

    register()
    if 'DEBUG_MODE' in sys.argv:
        debug()
