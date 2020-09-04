import sys
import os
import PyInstaller.__main__ as pyinstaller
import shutil
import zipfile
import cfg
from platform import architecture
import re
from site import getsitepackages


def return_hook_backup():
    print("Returning hook backup back")
    try:
        os.replace(backup_path, hook_path)
    except Exception as ex:
        print("haha loh. error is happened.")
        print(ex)
        return False
    else:
        print("backup returned")
        return True


def save_exit(code):
    if hook_modifying and not already_returned:
        return_hook_backup()
    sys.exit(code)


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                                GET ARGUMENTS                                #

args = sys.argv[1:]
MAKE_ZIP = '--make-zip' in args
ADD_ICON = '--add-icon' in args

if cfg.platform == 'unknown':
    print('Unknown platform:', sys.platform)
    save_exit(0)
print('Run on:', cfg.platform)

spec_path = os.path.join('arch', cfg.platform + '.spec')
NAME = 'problem-chooser-v' + cfg.VERSION + '-' + cfg.platform
if cfg.platform == 'win':
    NAME += architecture()[0][:2]

#                                                                             #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                                BUILD PREPARE                                #

hook_modifying = False
already_returned = False
hook_path = ""
backup_path = ""

shutil.rmtree(NAME, ignore_errors=True)
shutil.rmtree('build', ignore_errors=True)
shutil.rmtree('dist', ignore_errors=True)

if cfg.platform == 'mac':
    print("Running tkinter hook trick:")
    spdir = getsitepackages()[-1]
    hook_path = os.path.join(spdir, 'PyInstaller', 'hooks', 'hook-_tkinter.py')
    if not os.path.exists(hook_path):
        print('Press F. Hook not found in:')
        print(hook_path)
        save_exit(1)
    with open(hook_path, 'r') as hookfile:
        hook = hookfile.read()
    line_a = "if 'Library/Frameworks' in path_to_tcl"
    line_b = line_a + " and 'Python' not in path_to_tcl"
    line_a_count = hook.count(line_a)
    line_b_count = hook.count(line_b)
    if line_a_count != 1:
        print("Press F. Needed line is found " + str(line_a_count) + " times.")
        save_exit(1)
    if not line_b_count == 0:
        print("Kek. Hook is already modified. Skip...")
    else:
        hook = hook.replace(line_a, line_b)
        backup_path = hook_path + '.backup'
        try:
            shutil.copy(hook_path, backup_path)
        except Exception as ex:
            print("Press F. Making backup error.")
            print(ex)
            save_exit(1)
        else:
            hook_modifying = True
        try:
            with open(hook_path, "w") as hookfile:
                hookfile.write(hook)
        except Exception as ex:
            print("Press F. Writing modified hook error.")
            print(ex)
            save_exit(1)
        print("Modified!")

#                                                                             #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                                  BUILDING                                   #

print("\nBUILDING...")
try:
    pyinstaller.run([spec_path])
except Exception as ex:
    print("\nBUILDING FAILED\n")
    print(ex)
    save_exit(1)
else:
    print('BUILD FINISHED')
    already_returned = return_hook_backup()

#                                                                             #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                                BUILD FINISH                                 #


shutil.rmtree('build')
shutil.move('dist', NAME)

if os.path.exists(os.path.join(NAME, 'dist')):
    print('\nOOOPS!\nBug with "dist" instead of "problem-chooser"')
    save_exit(1)

#                                                                             #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                                 FILE TRICKS                                 #

dirname = "problem-chooser"

if cfg.platform == 'win':
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
    shutil.move(os.path.join(exec_loc, 'PyQt5', 'Qt', 'plugins', 'platforms'),
                os.path.join(exec_loc, 'platforms'))
elif cfg.platform == 'mac':
    shutil.rmtree(os.path.join(NAME, dirname), ignore_errors=True)
    dirname = "problem-chooser.app"

#                                                                             #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                              ADD ICON TO EXE                                #

if ADD_ICON:
    if cfg.platform == 'win':
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
            save_exit(return_code)
    else:
        print("--add-icon doesn't make sense on " + cfg.platform)

#                                                                             #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                                  MAKE ZIP                                   #

if MAKE_ZIP:
    print("\nMaking zip")
    with zipfile.ZipFile(NAME + '.zip', 'w', zipfile.ZIP_DEFLATED) as z:
        for root, dirs, files in os.walk(NAME, followlinks=True):
            pth = os.path.join('.', *root.strip(os.sep).split(os.sep)[1:])
            print("Adding:", pth)
            z.write(root, pth)
            for f in files:
                filezippath = os.path.join(pth, f)
                print('Adding:', filezippath)
                z.write(os.path.join(root, f), filezippath)
    shutil.move(NAME + '.zip', NAME)

#                                                                             #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

print("\nCompleted!")
