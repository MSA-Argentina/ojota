try:
    import memcache
    memcache_imported = True
except:
    memcache_imported = False


class Cache(object):
    """The base Cache class.
    Stores the cached data in memory.
    """
    def set(self, name, elems):
        """Sets the data into cache.

        Arguments:
            name -- the cache name.
            elems -- the data to cache.
        """
        setattr(self, name, elems)

    def get(self, name):
        """Gets the data from cache.

        Arguments:
            name -- the cache name.
        """
        return getattr(self, name)

    def __contains__(self, name):
        """Returns True if a given element is cached.

        Arguments:
            name -- the cache name.
        """
        has_data = hasattr(self, name)
        return has_data

    def clear(self, name):
        return delattr(self, name)


class Memcache(Cache):
    """Stores the cached data in memcache."""
    def __init__(self, cache_location="127.0.0.1", port=11211,
                  expiration_time=None, debug=None):
        """Constructor for the Memcache class.

        Arguments:
            cache_location -- memcached URI. defaults to 127.0.0.1
            port -- memcached port. Defaults to 11211
            expiration_time -- memcache expiration time
            debug -- activate memcache debug. Defaults to None
        """
        if memcache_imported:
            self._mc = memcache.Client(["%s:%d" % (cache_location, port)],
                                       debug=debug)
            self.expiration_time = expiration_time
        else:
            raise Exception("In order to use Memcache as cache you should install the 'memcache' package")

    def set(self, name, elems):
        """Sets the data into cache.

        Arguments:
            name -- the cache name.
            elems -- the data to cache.
        """
        self._mc.set(str(name), memcache.pickle.dumps(elems), self.expiration_time)

    def get(self, name):
        """Gets the data from cache.

        Arguments:
            name -- the cache name.
        """
        return memcache.pickle.loads(self._mc.get(str(name)))

    def __contains__(self, name):
        """Returns True if a given element is cached.

        Arguments:
            name -- the cache name.
        """
        _in_cache = not self._mc.get(str(name)) is None
        return _in_cache


class DummyCache(Cache):
    """Dummy Cache class to be able to use no cache."""
    def set(self, name, elems):
        """Sets the data into cache.

        Arguments:
            name -- the cache name.
            elems -- the data to cache.
        """
        self._cache = elems

    def get(self, name):
        return self._cache

    def __contains__(self, name):
        return False
