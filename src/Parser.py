import _pickle as cPickle
import gzip
import appdirs
import os

import cfg
from src.Worker import EMPTY_FUNCTION


def get_cache_location(cls):
    location = cfg.CACHE_LOCATIONS[cls.__name__]
    location = appdirs.AppDirs(location).user_cache_dir
    return location


class Parser:

    @classmethod
    def from_cache(cls):
        location = get_cache_location(cls)
        if not cls.cache_exists():
            raise Exception('Cache file is not exists')
        with open(location, 'rb') as f:
            try:
                compressed_dump = f.read()
                dump = gzip.decompress(compressed_dump)
                return cPickle.loads(dump)
            except Exception:
                raise Exception('There are some problems with cache. Please '
                                'update the cache by get table from server.')

    def save_cache(self):
        location = get_cache_location(self.__class__)
        dirlocation = os.path.dirname(location)
        if not os.path.exists(dirlocation):
            os.makedirs(dirlocation)
        with open(location, 'wb') as f:
            dump = cPickle.dumps(self)
            compressed_dump = gzip.compress(dump)
            f.write(compressed_dump)

    @classmethod
    def cache_exists(cls):
        location = get_cache_location(cls)
        return os.path.exists(location)

    @classmethod
    def delete_cache(cls):
        location = get_cache_location(cls)
        if cls.cache_exists():
            os.remove(location)

    @classmethod
    def from_server(cls, *args, **kwargs):
        p = cls(*args, **kwargs)
        p.set_from_server()
        return p

    def isReloading(self):
        return self.reload_worker.isRunning()

    def reload(self, on_finished=EMPTY_FUNCTION):
        self.reload_worker(self.set_from_server, on_finished)
