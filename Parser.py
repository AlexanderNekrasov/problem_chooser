import cachepath
import _pickle as cPickle
import gzip
from Worker import EMPTY_FUNCTION

CACHE_LOCATIONS = {'TableParser': 'problem_chooser_saved_table',
                   'MainPageParser': 'problem_chooser_main_page'}


def get_location(location, cls):
    if location is None:
        return CACHE_LOCATIONS[cls.__name__]
    else:
        return location


class Parser:
    @classmethod
    def from_cache(cls, location=None):
        location = get_location(location, cls)
        with cachepath.CachePath(location) as f:
            if not f.exists():
                raise Exception('Cache file is not exists')
            try:
                comp_bts = f.read_bytes()
                bts = gzip.decompress(comp_bts)
                return cPickle.loads(bts)
            except Exception:
                raise Exception('There are some problems with cache. Please '
                                'update the cache by get table from server.')

    def save_cache(self, location=None):
        location = get_location(location, self.__class__)
        with cachepath.CachePath(location) as f:
            bts = cPickle.dumps(self)
            comp_bts = gzip.compress(bts)
            f.write_bytes(comp_bts)

    @classmethod
    def is_cache_exists(cls, location=None):
        location = get_location(location, cls)
        return cachepath.CachePath(location).exists()

    @classmethod
    def delete_cache(cls, location=None):
        location = get_location(location, cls)
        return cachepath.CachePath(location).rm()

    @classmethod
    def from_server(cls, *args, **kwargs):
        p = cls(*args, **kwargs)
        p.set_from_server()
        return p

    def isReloading(self):
        return self.reload_worker.isRunning()

    def reload(self, on_finished=EMPTY_FUNCTION):
        self.reload_worker(self.set_from_server, on_finished)
