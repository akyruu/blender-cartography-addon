import os
import platform
import sys

print('Python version  : ' + platform.python_version())
print('Script arguments: ' + ' '.join(arg for i, arg in enumerate(sys.argv) if i > sys.argv.index('--')))

folder = '.'
if folder not in sys.path:
    sys.path.append(folder)

init_file = '__init__.py'

sys.argv.extend(['DEBUG_MODE'])
exec(compile(open(os.path.join(folder, init_file)).read(), init_file, 'exec'))
