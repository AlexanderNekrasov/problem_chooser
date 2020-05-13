import sys
import os
import shutil
import zipfile
from pkg_resources import require
import cfg

args = sys.argv[1:]
MAKE_ZIP = '--make-zip' in args
INSTALL_REQUIRMENTS = '--install-reqs' in args

NAME = 'problem-chooser-v' + cfg.VERSION

if INSTALL_REQUIRMENTS:
    print("Installing requirements.txt")
    os.system(sys.executable + " -m pip install -r requirements.txt")

require(open('requirements.txt').read().strip().split('\n'))

shutil.rmtree(NAME, ignore_errors=True)
print("\nBUILDING...")
exit_code = os.system(sys.executable +
                      ' -m PyInstaller -F main.py --clean --noconsole')
if exit_code:
    print("\nBUILDING FAILED")
    sys.exit(exit_code)
shutil.rmtree('build')
os.remove('main.spec')
os.rename(os.path.join('dist', 'main'), os.path.join('dist', 'prolem-chooser'))
shutil.move('dist', NAME)

if MAKE_ZIP:
    print("\nMaking zip")
    with zipfile.ZipFile(NAME + '.zip', 'w') as z:
        for root, dirs, files in os.walk(NAME):
            for f in files:
                z.write(os.path.join(root, f))

    shutil.move(NAME + '.zip', NAME)

print("\nBuild complete")
