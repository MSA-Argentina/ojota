import os

from unittest.case import TestCase

from ojota import Ojota
from ojota.base import set_data_source, current_data_code
from ojota.sources import Source, JSONSource, YAMLSource


class SourceTest(TestCase):
    def test_init(self):
        """Testing the init for Source."""
        expected = "data_path"
        source = Source(expected)
        result = source.data_path

        self.assertEqual(expected, result)

    def test_get_file_path(self):
        """Getting file path."""
        set_data_source("data")
        expected = "data/Ojotas"
        source = Source()
        result = source._get_file_path(Ojota)

        self.assertEqual(expected, result)

    def test_get_file_path_param(self):
        """Getting file path with a data_path param."""
        set_data_source("data")
        expected = "data_2/Ojotas"
        source = Source("data_2")
        result = source._get_file_path(Ojota)

        self.assertEqual(expected, result)

    def test_get_file_path_not_root(self):
        """Getting file path with data not in root."""
        current_data_code("data_code")

        class _OjotaChild(Ojota):
            data_in_root = False
            plural_name = "Ojotas"

        set_data_source("data")
        expected = "data/data_code/Ojotas"
        source = Source()
        result = source._get_file_path(_OjotaChild)

        self.assertEqual(expected, result)

    def test_get_file_path_param_not_root(self):
        """Getting file path with a data_path param and data not in root."""
        current_data_code("data_code")

        class _OjotaChild(Ojota):
            data_in_root = False
            plural_name = "Ojotas"

        set_data_source("data")
        expected = "data_2/data_code/Ojotas"
        source = Source("data_2")
        result = source._get_file_path(_OjotaChild)

        self.assertEqual(expected, result)

    def test_fetch_elements(self):
        """Getting fetch_elements."""
        source = Source()
        self.assertRaises(NotImplementedError, source.fetch_elements, Ojota)

    def test_fetch_element(self):
        """Getting fetch_element."""
        source = Source()
        self.assertRaises(NotImplementedError, source.fetch_element, Ojota, 1)


class JsonSourceTest(TestCase):
    def test_read_elements(self):
        """Testing the element loading from JSON."""
        file_path = (os.path.dirname(os.path.abspath(__file__)))
        set_data_source(os.path.join(file_path, "data"))

        class Person(Ojota):
            pk_field = "id"

        expected = {u'1': {u'name': u'Ezequiel', u'age': 25,
                           u'country_id': u'1', u'height': 120,
                           u'team_id': u'1', u'address': u'Lujan 1432',
                           u'id': u'1'},
                    u'3': {u'name': u'Juan Carlos', u'age': 35,
                           u'country_id': u'0', u'team_id': u'1',
                           u'address': u'Spam 3092', u'id': u'3'},
                    u'2': {u'name': u'Matias', u'age': 35, u'country_id': u'1',
                           u'team_id': u'2', u'address': u'Che Guevara 1875',
                           u'id': u'2'}}

        source = JSONSource()
        result = source.read_elements(Person, source._get_file_path(Person))
        self.assertEqual(expected, result)


class YAMLSourceTest(TestCase):
    def test_read_elements(self):
        """Testing the element loading from YAML."""
        file_path = (os.path.dirname(os.path.abspath(__file__)))
        set_data_source(os.path.join(file_path, "data"))

        class Team(Ojota):
            pk_field = "id"

        expected = {'1': {'color': 'red', 'id': '1', 'name': 'River Plate'},
                    '2': {'color': 'blue', 'id': '2', 'name': 'Boca Juniors'}}

        source = YAMLSource()
        result = source.read_elements(Team, source._get_file_path(Team))
        self.assertEqual(expected, result)