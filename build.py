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
