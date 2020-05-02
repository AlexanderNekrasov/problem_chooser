from sys import exit
from os import system, remove
from os.path import isdir

try:
    import shutil
except (ImportError, ModuleNotFoundError):
    print('Please, install shutil')
    print('pip install shutil --user')
    exit(0)

try:
    import PyInstaller
except (ImportError, ModuleNotFoundError):
    print('Please, install PyInstaller')
    print('pip install pyinstaller --user')
    exit(0)

if isdir('dist'):
    print('removing dist/')
    shutil.rmtree('dist')
    print('successfully removed')

system('pyinstaller -F main.py')

shutil.rmtree('build')
shutil.rmtree('__pycache__')
remove('main.spec')
shutil.copytree('data', 'dist/data')

print('all files in dist/')
