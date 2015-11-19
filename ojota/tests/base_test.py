from __future__ import absolute_import
import os

from unittest.case import TestCase

from ojota import Ojota, current_data_code
from ojota.base import set_data_source, Relation
from ojota.sources import Source, YAMLSource
from ojota.cache import DummyCache, Cache


class Person(Ojota):
    pk_field = "id"
    cache = DummyCache()


class Team(Ojota):
    pk_field = "id"
    data_source = YAMLSource()


class OjotaTest(TestCase):
    def setUp(self):
        TestCase.setUp(self)
        file_path = (os.path.dirname(os.path.abspath(__file__)))
        set_data_source(os.path.join(file_path, "data"))

    def test_repr(self):
        """Testing repr."""
        expected = "Person<1>"
        person = Person.one('1')
        self.assertEqual(expected, str(person))

    def test_all(self):
        """Testing the all method."""
        expected_len = 3
        expected_order = ['1', '2', '3']
        persons = Person.all()
        print(persons)
        self.assertEqual(expected_len, len(persons))
        result = [person.primary_key for person in persons]
        self.assertEqual(expected_order, sorted(result))

    def test_all_order(self):
        """Testing the all method with order."""
        expected_len = 3
        expected_order = ['1', '2', '3']
        persons = Person.many(sorted="id")
        self.assertEqual(expected_len, len(persons))
        result = [person.primary_key for person in persons]
        self.assertEqual(expected_order, result)

    def test_all_reverse_order(self):
        """Testing the all method with reverse order."""
        expected_len = 3
        expected_order = ['3', '2', '1']
        persons = Person.many(sorted="-id")
        self.assertEqual(expected_len, len(persons))
        result = [person.primary_key for person in persons]
        self.assertEqual(expected_order, result)

    def test_all_multiple_order(self):
        """Testing the all method with multiple order."""
        expected_len = 3
        expected_order = ['3', '1', '2']
        persons = Person.many(sorted="country_id,-address")
        self.assertEqual(expected_len, len(persons))
        result = [person.primary_key for person in persons]
        self.assertEqual(expected_order, result)

    def test_all_with_filters(self):
        """Testing the all method with filters."""
        expected_len = 1
        expected_order = ['1']
        persons = Person.many(id='1')
        self.assertEqual(expected_len, len(persons))
        result = [person.primary_key for person in persons]
        self.assertEqual(expected_order, result)

    def test_get_pk(self):
        """Testing the get method with pk."""
        pk = '1'
        person = Person.one(pk)
        self.assertEqual(pk, person.primary_key)

    def test_get_pk_param(self):
        """Testing the get method with pk as param."""
        pk = '1'
        person = Person.one(pk=pk)
        self.assertEqual(pk, person.primary_key)

        person = Person.one(id=pk)
        self.assertEqual(pk, person.primary_key)

    def test_get_wrong_pk(self):
        """Testing the get method with wrong pk."""
        pk = '0'
        person = Person.one(pk=pk)
        self.assertIsNone(person)

    def test_raise_one_error(self):
        """Testing the get method with no pk."""
        self.assertRaises(IndexError, Person.one)

    def test_get_no_pk_no_result(self):
        """Testing the get method that has no result."""
        person = Person.one(country_id='10')
        self.assertIsNone(person)

    def test_get_with_cmd(self):
        """Testing the get method with get_cmd enabled."""
        class MockSource(Source):
            get_cmd = None

            def read_element(self, cls, url, pk):
                return {'1': {'name': 'Ezequiel', 'age': 25,
                           'country_id': '1', 'height': 120,
                           'team_id': '1', 'address': 'Lujan 1432',
                           'id': '1'}}

        class Person(Ojota):
            pk_field = "id"
            data_source = MockSource()

        pk = '1'
        person = Person.one(pk)
        self.assertEqual(pk, person.primary_key)

    def test_eq(self):
        """Testing equality between Ojota classes."""
        person1a = Person.one('1')
        person1b = Person.one('1')
        person2 = Person.one('2')
        team = Team.one('1')

        self.assertEqual(person1a, person1b)
        self.assertNotEqual(person1a, person2)
        self.assertNotEqual(person1a, team)

    def test_to_dict(self):
        """Testing to_dict."""
        expected = {'name': 'Ezequiel', 'age': 25, 'country_id': '1',
                    'height': 120, 'team_id': '1', 'address': 'Lujan 1432',
                    'id': '1'}
        person = Person.one('1')
        result = person.to_dict()
        self.assertEqual(expected, result)

    def test_init(self):
        """Testing object initialization."""
        expected = {'name': 'Ezequiel', 'age': 25, 'country_id': '1',
                    'height': 120, 'team_id': '1', 'address': 'Lujan 1432',
                    'id': '1'}

        person = Person(**expected)
        self.assertEqual(expected, person.to_dict())
        self.assertEqual(sorted(list(expected.keys())), sorted(person.fields))

        for key in list(expected.keys()):
            self.assertTrue(hasattr(person, key))

    def test_init_required(self):
        """Testing object init with no params."""
        self.assertRaises(AttributeError, Person)

    def test_init_required_fields_id(self):
        """Testing required fields with id."""
        expected = {'id': '1'}

        person = Person(**expected)
        self.assertEqual(['id'], person.required_fields)

    def test_init_required_fields_tuple(self):
        """Testing required fields with id as a tuple."""
        expected = {'id': '1'}
        Person.required_fields = ('id', )
        person = Person(**expected)
        self.assertEqual(['id'], person.required_fields)

    def test_init_required_fields(self):
        """Testing required fields default pk addition."""
        expected = {'id': '1', "name": "Ezequiel"}

        person = Person(**expected)
        self.assertEqual(['id'], person.required_fields)

    def test_read_all_from_datasource(self):
        """Testing read all the data from datasource."""
        expected = {'1': {'name': 'Ezequiel', 'age': 25, 'country_id': '1',
                           'height': 120, 'team_id': '1', 'address':
                           'Lujan 1432', 'id': '1'},
                    '3': {'name': 'Juan Carlos', 'age': 35,
                           'country_id': '0', 'team_id': '1', 'address':
                           'Spam 3092', 'id': '3'},
                    '2': {'name': 'Matias', 'age': 35, 'country_id': '1',
                           'team_id': '2', 'address': 'Che Guevara 1875',
                           'id': '2'}}

        elements = Person._read_all_from_datasource()

        self.assertEqual(expected, elements)

    def test_read_all_from_datasource_cache(self):
        """Testing read all the data from datasource using cache."""
        class Person2(Person):
            plural_name = "Persons"
            cache = Cache()

        expected = {'1': {'name': 'Ezequiel', 'age': 25, 'country_id': '1',
                           'height': 120, 'team_id': '1', 'address':
                           'Lujan 1432', 'id': '1'},
                    '3': {'name': 'Juan Carlos', 'age': 35,
                           'country_id': '0', 'team_id': '1', 'address':
                           'Spam 3092', 'id': '3'},
                    '2': {'name': 'Matias', 'age': 35, 'country_id': '1',
                           'team_id': '2', 'address': 'Che Guevara 1875',
                           'id': '2'}}

        elements = Person2._read_all_from_datasource()
        self.assertEqual(expected, elements)
        elements = Person2._read_all_from_datasource()
        self.assertEqual(expected, elements)


    def test_read_all_from_datasource_not_in_root(self):
        """Testing read all the data from datasource with data not in root."""
        current_data_code("alternative")
        class Person2(Person):
            data_in_root = False
            plural_name = "Persons"

        expected = {'1': {'id': '1', 'name': 'Jhon'},
                    '2': {'id': '2', 'name': 'Paul'},
                    '3': {'id': '3', 'name': 'George'},
                    '4': {'id': '4', 'name': 'Ringo'}}

        elements = Person2._read_all_from_datasource()

        self.assertEqual(expected, elements)
        current_data_code("")

    def test_read_item_from_datasource(self):
        """Testing read one element from datasource."""
        expected = {'1': {'name': 'Ezequiel', 'age': 25,
                           'country_id': '1', 'height': 120,
                           'team_id': '1', 'address': 'Lujan 1432',
                           'id': '1'}}

        class MockSource(Source):
            @staticmethod
            def read_element(cls, *args, **kwargs):
                return expected

        class Person2(Person):
            data_source = MockSource()
            plural_name = "Persons"

        elements = Person2._read_item_from_datasource('1')

        self.assertEqual(expected['1'], elements)


    def test_read_item_from_datasource_cache(self):
        """Testing read one element from datasource using cache."""
        expected = {'1': {'name': 'Ezequiel', 'age': 25,
                           'country_id': '1', 'height': 120,
                           'team_id': '1', 'address': 'Lujan 1432',
                           'id': '1'}}

        class MockSource(Source):
            @staticmethod
            def read_element(cls, *args, **kwargs):
                return expected

        class Person2(Person):
            data_source = MockSource()
            plural_name = "Persons"
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
        """Testing expressions."""
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
        """Testing field does not exist."""
        self.assertFalse(Person._test_expression("name__endswith", "uan", {}))

    def test_no_operation(self):
        """Testing operation does not exist."""
        self.assertRaises(AttributeError, Person._test_expression,
                          "name__blah", "uan", {"name": "juan"})


class RelationsTest(TestCase):
    def setUp(self):
        TestCase.setUp(self)
        file_path = (os.path.dirname(os.path.abspath(__file__)))
        set_data_source(os.path.join(file_path, "data"))

    def test_init(self):
        """Testing init for relations."""
        attr_fk = "one"
        to_class = "two"
        related_name = "three"
        relation = Relation(attr_fk, to_class, related_name)
        self.assertEqual(attr_fk, relation.attr_fk)
        self.assertEqual(to_class, relation.to_class)
        self.assertEqual(related_name, relation.related_name)

    def test_relation(self):
        """Testing relation."""
        class Person2(Person):
            team = Relation("team_id", Team)
            plural_name = "Persons"

        person = Person2.one('1')
        self.assertEqual('1', person.team.primary_key)

    def test_reverse_relation(self):
        """Testing relation backwards."""
        class Person2(Person):
            team = Relation("team_id", Team, "persons")
            plural_name = "Persons"
            default_order = "id"

        person = Person2.one('1')
        self.assertEqual('1', person.team.primary_key)

        persons = Team.one('1').persons

        self.assertEqual(2, len(persons))
        self.assertEqual('1', persons[0].id)
        self.assertEqual('3', persons[1].id)
