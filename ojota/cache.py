try:
    import memcache
    memcache_imported = True
except:
    memcache_imported = False

class Cache(object):
    def set(self, name, elems):
        setattr(self, name, elems)

    def get(self, name):
        return getattr(self, name)

    def __contains__(self, name):
        has_data = hasattr(self, name)
        return has_data


class Memcache(Cache):
    def __init__(self, cache_location="127.0.0.1", port=11211, debug=None):
        if memcache_imported:
            self._mc = memcache.Client(["%s:%d" % (cache_location, port)],
                                       debug=debug)
        else:
            raise Exception("In order to use Memcache as cache you should install the 'memcache' package")

    def set(self, name, elems):
        self._mc.set(str(name), memcache.pickle.dumps(elems))

    def get(self, name):
        return memcache.pickle.loads(self._mc.get(str(name)))

    def __contains__(self, name):
        _in_cache = not self._mc.get(str(name)) is None
        return _in_cache


class DummyCache(Cache):
    def set(self, name, elems):
        self._cache = elems

    def get(self, name):
        return self._cache

    def __contains__(self, name):
        return False
