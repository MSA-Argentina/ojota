import os

from unittest.case import TestCase

from ojota import Ojota, current_data_code
from ojota.base import set_data_source
from ojota.sources import Source, YAMLSource
from ojota.cache import DummyCache, Cache


class Person(Ojota):
    plural_name = "Persons"
    pk_field = "id"
    cache = DummyCache()


class Team(Ojota):
    plural_name = "Teams"
    pk_field = "id"
    data_source = YAMLSource()


class OjotaTest(TestCase):
    def setUp(self):
        TestCase.setUp(self)
        file_path = (os.path.dirname(os.path.abspath(__file__)))
        set_data_source(os.path.join(file_path, "data"))

    def test_all(self):
        expected_len = 3
        expected_order = [u'1', u'3', u'2']
        persons = Person.all()
        self.assertEqual(expected_len, len(persons))
        result = [person.primary_key for person in persons]
        self.assertEqual(expected_order, result)

    def test_all_order(self):
        expected_len = 3
        expected_order = [u'1', u'2', u'3']
        persons = Person.all(sorted="id")
        self.assertEqual(expected_len, len(persons))
        result = [person.primary_key for person in persons]
        self.assertEqual(expected_order, result)

    def test_all_reverse_order(self):
        expected_len = 3
        expected_order = [u'3', u'2', u'1']
        persons = Person.all(sorted="-id")
        self.assertEqual(expected_len, len(persons))
        result = [person.primary_key for person in persons]
        self.assertEqual(expected_order, result)

    def test_all_multiple_order(self):
        expected_len = 3
        expected_order = [u'3', u'1', u'2']
        persons = Person.all(sorted="country_id,-address")
        self.assertEqual(expected_len, len(persons))
        result = [person.primary_key for person in persons]
        self.assertEqual(expected_order, result)

    def test_all_with_filters(self):
        expected_len = 1
        expected_order = [u'1']
        persons = Person.all(id='1')
        self.assertEqual(expected_len, len(persons))
        result = [person.primary_key for person in persons]
        self.assertEqual(expected_order, result)

    def test_get_pk(self):
        pk = '1'
        person = Person.get(pk)
        self.assertEqual(pk, person.primary_key)

    def test_get_pk_param(self):
        pk = '1'
        person = Person.get(pk=pk)
        self.assertEqual(pk, person.primary_key)

        person = Person.get(id=pk)
        self.assertEqual(pk, person.primary_key)

    def test_get_wrong_pk(self):
        pk = '0'
        person = Person.get(pk=pk)
        self.assertIsNone(person)

    def test_get_no_pk(self):
        pk = '1'
        person = Person.get(country_id='1')
        self.assertEqual(pk, person.primary_key)

    def test_get_no_pk_no_result(self):
        pk = '1'
        person = Person.get(country_id='10')
        self.assertIsNone(person)

    def test_get_with_cmd(self):
        class MockSource(Source):
            get_cmd = None

            def read_element(self, cls, url, pk):
                return {u'1': {u'name': u'Ezequiel', u'age': 25,
                           u'country_id': u'1', u'height': 120,
                           u'team_id': u'1', u'address': u'Lujan 1432',
                           u'id': u'1'}}

        class Person(Ojota):
            plural_name = "Persons"
            pk_field = "id"
            data_source = MockSource()

        pk = '1'
        person = Person.get(pk)
        self.assertEqual(pk, person.primary_key)

    def test_eq(self):
        person1a = Person.get('1')
        person1b = Person.get('1')
        person2 = Person.get('2')
        team = Team.get('1')

        self.assertEqual(person1a, person1b)
        self.assertNotEqual(person1a, person2)
        self.assertNotEqual(person1a, team)

    def test_to_dict(self):
        expected = {u'name': u'Ezequiel', u'age': 25, u'country_id': u'1',
                    u'height': 120, u'team_id': u'1', u'address': u'Lujan 1432',
                    u'id': u'1'}
        person = Person.get('1')
        result = person.to_dict()
        self.assertEqual(expected, result)

    def test_init(self):
        expected = {u'name': u'Ezequiel', u'age': 25, u'country_id': u'1',
                    u'height': 120, u'team_id': u'1', u'address': u'Lujan 1432',
                    u'id': u'1'}

        person = Person(**expected)
        self.assertEqual(expected, person.to_dict())
        self.assertEqual(expected.keys(), person.fields)

        for key in expected.keys():
            self.assertTrue(hasattr(person, key))

    def test_init_required(self):
        self.assertRaises(AttributeError, Person)

    def test_init_required_fields_id(self):
        expected = {u'id': u'1'}

        person = Person(**expected)
        self.assertEqual(['id'], person.required_fields)

    def test_init_required_fields(self):
        expected = {u'id': u'1', "name": "Ezequiel"}

        person = Person(**expected)
        self.assertEqual(['id'], person.required_fields)

    def test_read_all_from_datasource(self):
        expected = {u'1': {u'name': u'Ezequiel', u'age': 25, u'country_id': u'1',
                           u'height': 120, u'team_id': u'1', u'address':
                           u'Lujan 1432', u'id': u'1'},
                    u'3': {u'name': u'Juan Carlos', u'age': 35,
                           u'country_id': u'0', u'team_id': u'1', u'address':
                           u'Spam 3092', u'id': u'3'},
                    u'2': {u'name': u'Matias', u'age': 35, u'country_id': u'1',
                           u'team_id': u'2', u'address': u'Che Guevara 1875',
                           u'id': u'2'}}

        elements = Person._read_all_from_datasource()

        self.assertEqual(expected, elements)

    def test_read_all_from_datasource_not_in_root(self):
        current_data_code("alternative")
        class Person2(Person):
            data_in_root = False

        expected = {u'1': {u'id': u'1', u'name': u'Jhon'},
                    u'2': {u'id': u'2', u'name': u'Paul'},
                    u'3': {u'id': u'3', u'name': u'George'},
                    u'4': {u'id': u'4', u'name': u'Ringo'}}

        elements = Person2._read_all_from_datasource()

        self.assertEqual(expected, elements)
        current_data_code("")

    def test_read_item_from_datasource(self):
        expected = {u'1': {u'name': u'Ezequiel', u'age': 25,
                           u'country_id': u'1', u'height': 120,
                           u'team_id': u'1', u'address': u'Lujan 1432',
                           u'id': u'1'}}

        class MockSource(Source):
            @staticmethod
            def read_element(cls, *args, **kwargs):
                return expected

        class Person2(Person):
            data_source = MockSource()

        elements = Person2._read_item_from_datasource('1')

        self.assertEqual(expected['1'], elements)


    def test_read_item_from_datasource_cache(self):
        expected = {u'1': {u'name': u'Ezequiel', u'age': 25,
                           u'country_id': u'1', u'height': 120,
                           u'team_id': u'1', u'address': u'Lujan 1432',
                           u'id': u'1'}}

        class MockSource(Source):
            @staticmethod
            def read_element(cls, *args, **kwargs):
                return expected

        class Person2(Person):
            data_source = MockSource()
            cache = Cache()

        elements = Person2._read_item_from_datasource('1')

        self.assertEqual(expected['1'], elements)

        elements = Person2._read_item_from_datasource('1')
        self.assertEqual(expected['1'], elements)



class ExpressionTest(TestCase):
    def _test_expression(self, expresion, value, element_data, should_return):
        result = Person._test_expression(expresion, value, element_data)
        self.assertEqual(should_return, result)
    def test_expressions(self):
        expresions = [
            ("name", "juan", {'name': "juan"}, True),
            ("name", "juan", {'name': "pedro"}, False),

            ("name__exact", "juan", {'name': "juan"}, True),
            ("name__exact", "juan", {'name': "Juan"}, False),

            ("name__iexact", "juan", {'name': "juan"}, True),
            ("name__iexact", "juan", {'name': "Juan"}, True),
            ("name__iexact", "juan", {'name': "Pedro"}, False),

            ("name__contains", "uan", {'name': "juan"}, True),
            ("name__contains", "juan", {'name': "pedro"}, False),

            ("name__icontains", "uan", {'name': "juan"}, True),
            ("name__icontains", "UAN", {'name': "juan"}, True),
            ("name__icontains", "juan", {'name': "pedro"}, False),

            ("name__in", ("juan", "pedro"), {'name': "juan"}, True),
            ("name__in", ("pedro", "mario"), {'name': "juan"}, False),

            ("number__gt", 4, {'number': 5}, True),
            ("number__gt", 6, {'number': 5}, False),

            ("number__gte", 4, {'number': 5}, True),
            ("number__gte", 5, {'number': 5}, True),
            ("number__gte", 6, {'number': 5}, False),

            ("number__lt", 4, {'number': 5}, False),
            ("number__lt", 6, {'number': 5}, True),

            ("number__lte", 4, {'number': 5}, False),
            ("number__lte", 6, {'number': 5}, True),
            ("number__lte", 5, {'number': 5}, True),

            ("name__startswith", "jua", {'name': "juan"}, True),
            ("name__startswith", "jua", {'name': "pedro"}, False),

            ("name__istartswith", "jua", {'name': "Juan"}, True),
            ("name__istartswith", "jua", {'name': "juan"}, True),
            ("name__istartswith", "jua", {'name': "pedro"}, False),


            ("name__endswith", "uan", {'name': "juan"}, True),
            ("name__endswith", "uan", {'name': "pedro"}, False),

            ("name__iendswith", "uan", {'name': "JuaN"}, True),
            ("name__iendswith", "uan", {'name': "juan"}, True),
            ("name__iendswith", "uan", {'name': "pedro"}, False),

            ("number__range", (5, 10), {'number': 7}, True),
            ("number__range", (5, 10), {'number': 3}, False),
            ("number__range", (5, 10), {'number': 11}, False),

            ("name__ne", "juan", {'name': "juan"}, False),
            ("name__ne", "juan", {'name': "pedro"}, True),
        ]

        for expresion in expresions:
            self._test_expression(*expresion)

    def test_no_field(self):
        self.assertRaises(AttributeError, Person._test_expression,
                          "name__endswith", "uan", {})

    def test_no_operation(self):
        self.assertRaises(AttributeError, Person._test_expression,
                          "name__blah", "uan", {"name": "juan"})
























