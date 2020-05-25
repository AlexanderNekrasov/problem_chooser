import sys
import os
import PyInstaller.__main__ as pyinstaller
import shutil
import zipfile
import cfg


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                                GET ARGUMENTS                                #

args = sys.argv[1:]
MAKE_ZIP = '--make-zip' in args

NAME = 'problem-chooser-v' + cfg.VERSION

#                                                                             #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                           BUILD, CLEAN AND RENAME                           #

shutil.rmtree(NAME, ignore_errors=True)
shutil.rmtree('build', ignore_errors=True)
shutil.rmtree('dist', ignore_errors=True)

print("\nBUILDING...")
try:
    pyinstaller.run(['main.spec'])
except Exception as ex:
    print("\nBUILDING FAILED\n")
    print(ex)
    sys.exit(1)
else:
    print('BUILD FINISHED')

shutil.rmtree('build')
dirname = os.listdir('dist')[0]
newdirname = dirname.replace('main', 'problem-chooser')
os.rename(os.path.join('dist', dirname), os.path.join('dist', newdirname))
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

print("\nCompleted!")
