import os
import sys


class Path:
    root = sys.path[0]
    resources = os.path.join(root, 'resources')
    main = os.path.join(root, 'main.py')
    add_lib = os.path.join(root, 'arch', 'add_lib.py')


datas = []
for absroot, dirs, files in os.walk(Path.resources):
    root = absroot[len(Path.root + os.path.sep):]
    for file in files:
        datas.append((
            os.path.join(absroot, file),
            root
        ))
