"""
This file is part of Ojota.

    Ojota is free software: you can redistribute it and/or modify
    it under the terms of the GNU LESSER GENERAL PUBLIC LICENSE as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Ojota is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Lesser General Public License for more details.

    You should have received a copy of the GNU  Lesser General Public License
    along with Ojota.  If not, see <http://www.gnu.org/licenses/>.
"""
import json
import os

try:
    import yaml
except ImportError:
    pass


DATA_SOURCE = "data"


def current_data_code(data_code):
    """Sets the current data path."""
    Serializado.CURRENT_DATA_CODE = data_code


class Relation(object):
    """Adds a relation to another object."""
    def __init__(self, attr_fk, to_class, related_name=None):
        """Constructor for the relation class
        Arguments:
            attr_fk -- a String with the foreign key attribute name
            to_class -- the class that the relation makes reference to
            related_name -- the name of the attribute for the backward relation
                 Default None
        """
        self.attr_fk = attr_fk
        self.to_class = to_class
        self.related_name = related_name

    def get_property(self):
        """Returns the property in which the relation will be referenced."""
        def _inner(method_self):
            """Inner function to return the property for the relation."""
            fk = getattr(method_self, self.attr_fk)
            return self.to_class.get(fk)
        return property(_inner)

    def set_reversed_property(self, from_class):
        """Returns the property in which the backwards relation will be
        referenced."""
        def _inner(method_self):
            """Inner function to return the property for the backwards
            relation."""
            pk = method_self.primary_key
            params = {self.attr_fk: pk}
            return from_class.all(**params)

        if self.related_name:
            prop = property(_inner)
            setattr(self.to_class, self.related_name, prop)


class MetaSerializado(type):
    """Metaclass For the serializer"""
    def __init__(self, *args, **kwargs):
        for attr, value in self.__dict__.items():
            if isinstance(value, Relation):
                value.set_reversed_property(self)
                setattr(self, attr, value.get_property())
        return super(MetaSerializado, self).__init__(*args, **kwargs)


class Serializado(object):
    """Base class to create instances of serialized data in the source files."""
    __metaclass__ = MetaSerializado
    CURRENT_DATA_CODE = ''
    plural_name = 'Serializado'
    data_in_root = True
    pk_field = "pk"
    required_fields = None

    @property
    def primary_key(self):
        """Retruns the primary key value."""
        return getattr(self, self.pk_field)

    def __init__(self, _pk=None, **kwargs):
        """Constructor."""
        if self.required_fields is not None:
            _requeridos = list(self.required_fields)
            _requeridos.append(self.pk_field)

            if not all([key in kwargs for key in _requeridos]):
                raise AttributeError

        for key, val in kwargs.iteritems():
            setattr(self, key, val)

    @classmethod
    def _read_file(cls):
        """Reads the data form the file, makes a dictionary with the key
        specified in the key paramater. Allows to filter by subdirectories when
        the data is not on the root according to the data path."""
        cache_name = '_cache_' + cls.plural_name

        if not cls.data_in_root and Serializado.CURRENT_DATA_CODE:
            cache_name += '_' + Serializado.CURRENT_DATA_CODE

        if cache_name not in dir(cls):
            if cls.data_in_root or not Serializado.CURRENT_DATA_CODE:
                filepath = os.path.join(DATA_SOURCE,
                                         cls.plural_name)
            else:
                filepath = os.path.join(DATA_SOURCE,
                                         Serializado.CURRENT_DATA_CODE,
                                         cls.plural_name)
            try:
                elements = cls._read_json_elements(filepath)
            except IOError:
                elements = cls._read_yaml_elements(filepath)

            setattr(cls, cache_name, elements)
        return getattr(cls, cache_name)

    @classmethod
    def _read_json_elements(cls, filepath):
        """Reads the elements form a JSON file. Returns a dictionary containing
        the read data.

        Arguments:
        filepath -- the path for the json file.
        """
        data = json.load(open('%s.json' % filepath, 'r'))
        elements = dict((element_data[cls.pk_field], element_data)
                        for element_data in data)

        return elements

    @classmethod
    def _read_yaml_elements(cls, filepath):
        """Reads the elements form a YAML file. Returns a dictionary containing
        the read data.

        Arguments:
        filepath -- the path for the yaml file.
        """
        datos = yaml.load(open('%s.yaml' % filepath, 'r'))
        elements = {}
        for key, value in datos.items():
            elements[value[cls.pk_field]] = value

        return elements

    @classmethod
    def get(cls, pk=None, **kargs):
        """Returns the first element that matches the conditions."""
        if pk:
            kargs[cls.pk_field] = pk
        if kargs.keys() == [cls.pk_field]:
            pk = kargs[cls.pk_field]
            all_elems = cls._read_file()
            if pk in all_elems:
                return cls(**all_elems[pk])
            else:
                return None
        else:
            result = cls.all(**kargs)
            if result:
                return result[0]
            else:
                return None

    @classmethod
    def _objetize(cls, data):
        """Return the data into an element."""
        return [cls(**element_data) for element_data in data]

    @classmethod
    def _test_expression(cls, expression, value, element_data):
        """Finds out if a value in a given field matches an expression.

        Arguments:
        expression -- a string with the comparison expression. If the
        expression is a field name it will be compared with equal. In case that
        the field has "__" and an operation appended the it is compared with
        the appended expression. The availiable expressions allowed are: "=",
        "exact", "iexact", "contains", "icontains", "in", "gt", "gte", "lt",
        "lte", "startswith", "istartswith", "endswith", "iendswith", "range"
        and "ne"
        """
        partes_expression = expression.split('__')
        if len(partes_expression) == 1:
            field = expression
            operation = '='
        else:
            field, operation = partes_expression

        r = True
        try:
            if operation in ('=', 'exact'):
                r = element_data[field] == value
            elif operation == 'iexact':
                r = str(element_data[field]).lower() == str(value).lower()
            elif operation == 'contains':
                r = value in element_data[field]
            elif operation == 'icontains':
                r = str(value).lower() in str(element_data[field]).lower()
            elif operation == 'in':
                r = element_data[field] in value
            elif operation == 'gt':
                r = element_data[field] > value
            elif operation == 'gte':
                r = element_data[field] >= value
            elif operation == 'lt':
                r = element_data[field] < value
            elif operation == 'lte':
                r = element_data[field] <= value
            elif operation == 'startswith':
                r = str(element_data[field]).startswith(str(value))
            elif operation == 'istartswith':
                r = str(element_data[field]).lower().startswith(str(value).lower())
            elif operation == 'endswith':
                r = str(element_data[field]).endswith(str(value))
            elif operation == 'iendswith':
                r = str(element_data[field]).lower().endswith(str(value).lower())
            elif operation == 'range':
                r = value[0] <= element_data[field] <= value[1]
            elif operation == 'ne':
                r = element_data[field] != value
            else:
                raise AttributeError("The operation %s does not exist" % operation)
        except KeyError:
            raise AttributeError("The field %s does not exist" % field)
        # TODO date operations
        # TODO regex operations
        return r

    @classmethod
    def _filter(cls, data, filters):
        """Applies filter to data.

        Arguments:
            data -- an iterable containing the data
            filters -- a dictionary with the filters
        """
        filtrados = []
        for element_data in data:
            add = True
            for expression, value in filters.items():
                if not cls._test_expression(expression, value, element_data):
                    add = False
                    break
            if add:
                filtrados.append(element_data)

        return filtrados

    @classmethod
    def _sort(cls, data_list, order_fields):
        """Sort a list by a given field or field froups.

        Arguments:
            data_list -- a list with the data
            order_fields -- a string with the order fields
        """
        order_fields = [x.strip() for x in order_fields.split(',')]

        for order_field in reversed(order_fields):
            if order_field.startswith('-'):
                reverse = True
                order_field = order_field[1:]
            else:
                reverse = False

            data_list = sorted(data_list, key=lambda e: getattr(e, order_field),
                               reverse=reverse)
        return data_list

    @classmethod
    def all(cls, **kargs):
        """Returns all the elements that match the conditions."""
        elements = cls._read_file().values()
        order_fields = None
        if 'sorted' in kargs:
            order_fields = kargs['sorted']
            del kargs['sorted']

        if kargs:
            elements = cls._filter(elements, kargs)

        list_ = cls._objetize(elements)

        if order_fields:
            list_ = cls._sort(list_, order_fields)

        return list_

    def __eq__(self, other):
        """Compare the equality of two elements."""
        same_pk = self.primary_key == other.primary_key
        same_class = self.__class__ is other.__class__
        return same_pk and same_class

    def __repr__(self):
        """String representation of the elements."""
        return '%s<%s>' % (self.__class__.__name__, self.primary_key)

