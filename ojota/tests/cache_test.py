from __future__ import absolute_import
from unittest.case import TestCase

from ojota.cache import Cache, DummyCache


class CacheTest(TestCase):
    def test_set_get(self):
        """Testing Cache set and get."""
        key = "test"
        expected = "blah"

        cache = Cache()
        cache.set(key, expected)
        result = cache.get(key)
        self.assertEqual(expected, result)

    def test_get_inexistent(self):
        """Testing inexisting key in cache"""
        key = "test"

        cache = Cache()
        self.assertRaises(AttributeError, cache.get, key)

    def test_not_contains(self):
        """Testing not in cache."""
        key = "test"

        cache = Cache()
        self.assertNotIn(key, cache)

    def test_contains(self):
        """Testing in cache."""
        key = "test"

        cache = Cache()
        cache.set(key, "")
        self.assertIn(key, cache)


class DummyCacheTest(TestCase):
    def test_set_get(self):
        """testing DummyCache set and get."""
        key = "test"
        expected = "blah"

        cache = DummyCache()
        cache.set(key, expected)
        result = cache.get(key)
        self.assertEqual(expected, result)

    def test_get_inexistent(self):
        """Testing inexisting key in cache"""
        key = "test"

        cache = DummyCache()
        self.assertRaises(AttributeError, cache.get, key)

    def test_not_contains(self):
        """Testing not in cache."""
        key = "test"

        cache = DummyCache()
        self.assertNotIn(key, cache)

    def test_contains(self):
        """Testing in cache."""
        key = "test"

        cache = DummyCache()
        cache.set(key, "")
        self.assertNotIn(key, cache)
