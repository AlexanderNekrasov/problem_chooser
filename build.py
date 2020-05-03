NAME = 'problem-chooser-v1.0'


def try_import(lib, piplib=None):
    if piplib is None:
        piplib = lib
    try:
        lb = __import__(lib)
    except (ImportError, ModuleNotFoundError):
        print('Please, install ' + lib)
        print('Use something similar to this:')
        print('pip install ' + piplib + ' --user')
        exit(0)
    return lb


sys = try_import('sys')
os = try_import('os')
shutil = try_import('shutil')
zipfile = try_import('zipfile')
try_import('PyInstaller', 'pyinstaller')
try_import('PyQt5')
try_import('re')
try_import('requests')
try_import('bs4')


shutil.rmtree(NAME, ignore_errors=True)
os.system('pyinstaller -F main.py --clean')
shutil.rmtree('build')
os.remove('main.spec')
shutil.move('dist', NAME)


with zipfile.ZipFile(NAME + '.zip', 'w') as z:
    for root, dirs, files in os.walk(NAME):
        for f in files:
            z.write(os.path.join(root, f))


shutil.move(NAME + '.zip', NAME)

print('all files in ./' + NAME + '/')
