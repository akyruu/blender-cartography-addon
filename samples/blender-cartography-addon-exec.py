import os
import sys

scriptsFolder = "D:/Dev/Blender/@Scripts"
addonName = "blender-cartography-addon"

folder = os.path.join(scriptsFolder, addonName)
initFile = "__init__.py"

if folder not in sys.path:
    sys.path.append(folder)

file = os.path.join(folder, initFile)

if 'DEBUG_MODE' not in sys.argv:
    sys.argv.append('DEBUG_MODE')

exec(compile(open(file).read(), initFile, 'exec'))

if 'DEBUG_MODE' in sys.argv:
    sys.argv.remove('DEBUG_MODE')
