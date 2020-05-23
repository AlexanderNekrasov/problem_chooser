import sys
import os
import subprocess
import shutil
import zipfile
from pkg_resources import require, DistributionNotFound, VersionConflict
import cfg


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                                GET ARGUMENTS                                #

args = sys.argv[1:]
MAKE_ZIP = '--make-zip' in args

NAME = 'problem-chooser-v' + cfg.VERSION

#                                                                             #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                       INSTALL AND CHECK REQUIREMENTS                        #

print("Checking and installing requirements.txt")
subprocess.call(sys.executable + " -m pip install -r requirements.txt",
                shell=True)

try:
    require(open('requirements.txt').read().strip().split('\n'))
except (DistributionNotFound, VersionConflict) as ex:
    print('Check requirements failed:')
    print(' ', ex)
    print('Try again')
    exit(1)
except Exception as ex:
    print('Some errors found:\n')
    raise ex

#                                                                             #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                           BUILD, CLEAN AND RENAME                           #

shutil.rmtree(NAME, ignore_errors=True)
shutil.rmtree('build', ignore_errors=True)
shutil.rmtree('dist', ignore_errors=True)

print("\nBUILDING...")
exit_code = subprocess.call(
    sys.executable + ' -m PyInstaller main.spec', shell=True)

if exit_code:
    print("\nBUILDING FAILED")
    sys.exit(exit_code)

shutil.rmtree('build')

filename = os.listdir('dist')[0]
newfilename = filename.replace('main', 'problem-chooser')
os.rename(os.path.join('dist', filename), os.path.join('dist', newfilename))
shutil.move('dist', NAME)

#                                                                             #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                                  MAKE ZIP                                   #

if MAKE_ZIP:
    print("\nMaking zip")
    with zipfile.ZipFile(NAME + '.zip', 'w', zipfile.ZIP_DEFLATED) as z:
        for root, dirs, files in os.walk(NAME):
            pth = os.path.join('.', *root.strip(os.sep).split(os.sep)[1:])
            for f in files:
                filezippath = os.path.join(pth, f)
                print('Adding:', filezippath)
                z.write(os.path.join(root, f), filezippath)
    shutil.move(NAME + '.zip', NAME)

#                                                                             #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

print("\nBuild complete")
