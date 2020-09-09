import os
import sys

# Script location
scripts_folder = 'D:/Dev/Blender/@Scripts'
addon_name = 'blender-cartography-addon'

# Arguments
action = 'read_csv_file'
coords_name = 'coordinates_02.tsv'

# Execution
folder = os.path.join(scripts_folder, addon_name)
init_file = "__init__.py"
coords_file = os.path.join(scripts_folder, addon_name, 'samples', coords_name) if coords_name else None

sys.argv.extend(['DEBUG_MODE', '-a', action])
if coords_file:
    sys.argv.extend(['-f', coords_file])

if folder not in sys.path:
    sys.path.append(folder)
file = os.path.join(folder, init_file)

exec(compile(open(file).read(), init_file, 'exec'))
