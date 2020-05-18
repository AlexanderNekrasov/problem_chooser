import _pickle as cPickle
import gzip
import cachepath

import cfg
from src.Worker import EMPTY_FUNCTION


def get_cache_location(location, cls):
    if location is None:
        location = cfg.CACHE_LOCATIONS[cls.__name__]
    return location


class Parser:

    @classmethod
    def from_cache(cls, location=None):
        location = get_cache_location(location, cls)
        with cachepath.CachePath(location) as f:
            if not f.exists():
                raise Exception('Cache file is not exists')
            try:
                compressed_dump = f.read_bytes()
                dump = gzip.decompress(compressed_dump)
                return cPickle.loads(dump)
            except Exception:
                raise Exception('There are some problems with cache. Please '
                                'update the cache by get table from server.')

    def save_cache(self, location=None):
        location = get_cache_location(location, self.__class__)
        with cachepath.CachePath(location) as f:
            dump = cPickle.dumps(self)
            compressed_dump = gzip.compress(dump)
            f.write_bytes(compressed_dump)

    @classmethod
    def cache_exists(cls, location=None):
        location = get_cache_location(location, cls)
        return cachepath.CachePath(location).exists()

    @classmethod
    def delete_cache(cls, location=None):
        location = get_cache_location(location, cls)
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
