import sys
import os
import PyInstaller.__main__ as pyinstaller
import shutil
import zipfile
import cfg
from platform import architecture
import re

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                                GET ARGUMENTS                                #

args = sys.argv[1:]
MAKE_ZIP = '--make-zip' in args
ADD_ICON = '--add-icon' in args

if sys.platform in ('win32', 'cygwin'):
    platform = 'win'
elif sys.platform in ('linux',):
    platform = 'linux'
elif sys.platform in ('darwin',):
    platform = 'mac'
else:
    platform = 'unknown'
    print('Unknown platform:', sys.platform)
    exit(0)
print('Run on:', platform)

spec_path = os.path.join('arch', platform + '.spec')
NAME = 'problem-chooser-v' + cfg.VERSION + '-' + platform
if platform == 'win':
    NAME += architecture()[0][:2]

#                                                                             #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                           BUILD, CLEAN AND RENAME                           #

shutil.rmtree(NAME, ignore_errors=True)
shutil.rmtree('build', ignore_errors=True)
shutil.rmtree('dist', ignore_errors=True)

print("\nBUILDING...")
try:
    pyinstaller.run([spec_path])
except Exception as ex:
    print("\nBUILDING FAILED\n")
    print(ex)
    sys.exit(1)
else:
    print('BUILD FINISHED')

shutil.rmtree('build')
dirname = os.listdir('dist')[0]
shutil.move('dist', NAME)
if os.path.exists(os.path.join(NAME, 'dist')):
    print('\nOOOPS!\nBug with "dist" instead of "problem-chooser"')
    exit(1)

#                                                                             #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                             MOVING FILES TO LIB                             #

if platform == 'win':
    exec_loc = os.path.join(NAME, dirname)
    exec_path = os.path.join(exec_loc, 'problem-chooser.exe')
    lib_path = os.path.join(exec_loc, "lib")
    os.makedirs(lib_path)

    NEEDED_FILES = ["lib", "PyQt5", "certifi", "resources", "base_library.zip",
                    "problem-chooser.exe"]
    NEEDED_REGEX = ["python.*"]
    for name in os.listdir(exec_loc):
        is_needed = name in NEEDED_FILES
        for regex in NEEDED_REGEX:
            is_needed |= re.fullmatch(regex, name) is not None
        if not is_needed:
            print("Moving", os.path.join(exec_loc, name), "to lib")
            shutil.move(os.path.join(exec_loc, name), lib_path)
elif platform == 'linux':
    pass
elif platform == 'mac':
    pass

#                                                                             #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                              ADD ICON TO EXE                                #

if ADD_ICON:
    if platform == 'win':
        print("\nAdding icon")
        from subprocess import call

        rh_args = ['ResourceHacker.exe',
                   '-open', exec_path,
                   '-save', exec_path,
                   '-action', 'addskip',
                   '-res', cfg.resource('icon.ico'),
                   '-mask', 'ICONGROUP,MAINICON']
        return_code = call(' '.join(rh_args))
        if return_code:
            print('ResourceHacker error')
            exit(return_code)
    else:
        print("--add-icon doesn't make sense on " + platform)

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
