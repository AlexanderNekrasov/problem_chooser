from sys import exit
from os import system, remove
from os.path import isdir


def try_import(lib, piplib=None):
    if piplib is None:
        piplib = lib
    try:
        lb = __import__(lib)
    except (ImportError, ModuleNotFoundError):
        print('Please, install ' + lib)
        print('pip install ' + piplib + ' --user')
        exit(0)
    return lb


shutil = try_import('shutil')
try_import('PyInstaller', 'pyinstaller')
try_import('sfml')
try_import('re')
try_import('requests')
try_import('bs4')

NAME = 'problem-chooser-v1.0'

if isdir(NAME):
    print('removing ' + NAME)
    shutil.rmtree(NAME)
    print('successfully removed')

system('pyinstaller -F main.py')

shutil.rmtree('build')
shutil.rmtree('__pycache__', ignore_errors=True)
remove('main.spec')
shutil.copytree('data', 'dist/data')

shutil.move('dist', NAME)
shutil.make_archive(NAME, 'zip', NAME)
shutil.move(NAME + '.zip', NAME)

print('all files in problem-chooser-v1.0/')
