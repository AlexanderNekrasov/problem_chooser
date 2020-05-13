import sys
import os
import shutil
import zipfile
from pkg_resources import require, DistributionNotFound, VersionConflict
import cfg

args = sys.argv[1:]
MAKE_ZIP = '--make-zip' in args
NOT_INSTALL_REQUIRMENTS = '--not-install-reqs' in args

NAME = 'problem-chooser-v' + cfg.VERSION

if not NOT_INSTALL_REQUIRMENTS:
    print("Installing requirements.txt")
    os.system(sys.executable + " -m pip install -r requirements.txt")

try:
    require(open('requirements.txt').read().strip().split('\n'))
except (DistributionNotFound, VersionConflict) as ex:
    print('Check requirements failed:')
    print(' ', ex)
    print('Try again')
    exit(0)
except Exception as ex:
    print('Some errors found:\n')
    raise ex


shutil.rmtree(NAME, ignore_errors=True)
print("\nBUILDING...")
exit_code = os.system(sys.executable +
                      ' -m PyInstaller -F main.py --clean --noconsole')
if exit_code:
    print("\nBUILDING FAILED")
    sys.exit(exit_code)
shutil.rmtree('build')
os.remove('main.spec')

filename = os.listdir('dist')[0]
newfilename = filename.replace('main', 'problem-chooser')

os.rename(os.path.join('dist', filename), os.path.join('dist', newfilename))
shutil.move('dist', NAME)

if MAKE_ZIP:
    print("\nMaking zip")
    with zipfile.ZipFile(NAME + '.zip', 'w') as z:
        for root, dirs, files in os.walk(NAME):
            for f in files:
                z.write(os.path.join(root, f))

    shutil.move(NAME + '.zip', NAME)

print("\nBuild complete")
