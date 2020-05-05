NAME = 'problem-chooser-v1.0'


def try_import(lib, piplib=None):
    if piplib is None:
        piplib = lib
    try:
        return __import__(lib)
    except (ImportError, ModuleNotFoundError):
        print('Please, install ' + lib)
        print('Use something similar to this:')
        print('pip install ' + piplib + ' --user')
        exit(0)


import sys, os, shutil, zipfile

from pkg_resources import require
require(['PyInstaller>=3.6'])
require(open('requirements.txt').read().strip().split('\n'))

shutil.rmtree(NAME, ignore_errors=True)
os.system(sys.executable + ' -m PyInstaller -F main.py --clean')
shutil.rmtree('build')
os.remove('main.spec')
shutil.move('dist', NAME)

with zipfile.ZipFile(NAME + '.zip', 'w') as z:
    for root, dirs, files in os.walk(NAME):
        for f in files:
            z.write(os.path.join(root, f))

shutil.move(NAME + '.zip', NAME)

print('all files in ./' + NAME + '/')
