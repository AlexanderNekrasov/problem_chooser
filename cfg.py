from os import path

VERSION = '1.79'

TABLE_URL = 'https://server.179.ru/shashkov/stand_b22.php'
MAIN_PAGE_URL = "https://server.179.ru/wiki/?page=Informatika/9B"

CACHE_LOCATIONS = {'TableParser': path.join('problem_chooser', 'saved_table'),
                   'MainPageParser': path.join('problem_chooser', 'main_page')}
