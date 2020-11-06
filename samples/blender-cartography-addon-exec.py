import os
import sys

# Script location
scripts_folder = '/home/Cyril.Audibert/.perso/workspace/pycharm'
addon_name = 'blender-cartography-addon'

# Arguments
action = 'read_csv_file'
coords_name = 'coordinates_03.tsv'

# Execution
folder = os.path.join(scripts_folder, addon_name)
init_file = "__init__.py"

sys.argv.extend(['DEBUG_MODE', '-a', action])
if coords_name:
    sample_folder = os.path.join(folder, 'samples')
    coords_file = os.path.join(sample_folder, coords_name)
    export_file = os.path.join(sample_folder, coords_name.replace('.tsv', '.blend'))

    sys.argv.extend(['-f', coords_file])
    sys.argv.extend(['-e', export_file])

if folder not in sys.path:
    sys.path.append(folder)
file = os.path.join(folder, init_file)

exec(compile(open(file).read(), init_file, 'exec'))
