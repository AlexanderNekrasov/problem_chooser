from os import path
import sys
import appdirs

VERSION = '2.0.1'

TABLE_URL = 'https://server.179.ru/shashkov/stand_b22.php'
MAIN_PAGE_URL = "https://server.179.ru/wiki/?page=Informatika/10B"


def user_cache_dir(s):
    return appdirs.AppDirs(s).user_cache_dir


def user_data_dir(s):
    return appdirs.AppDirs(s).user_data_dir


CACHE_LOCATIONS = {'TableParser':
                   user_cache_dir(path.join('problem_chooser', 'saved_table')),
                   'MainPageParser':
                   user_cache_dir(path.join('problem_chooser', 'main_page'))}

CONFIG_LOCATION = user_data_dir(path.join('problem_chooser', 'config.json'))

COMPILED = hasattr(sys, 'frozen') and hasattr(sys, '_MEIPASS')

platform = {'win32': 'win',
            'cygwin': 'win',
            'linux': 'linux',
            'darwin': 'mac'}.get(sys.platform, 'unknown')


def resource(*args):
    relative_path = path.join('resources', *args)
    if COMPILED:
        base_path = path.join(sys._MEIPASS, ".." if platform == 'win' else ".")
    else:
        base_path = path.abspath(".")
    return path.join(base_path, relative_path)
