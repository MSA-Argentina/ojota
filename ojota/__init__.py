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

import os
import json

try:
    import yaml
except ImportError:
    pass

from urllib2 import urlopen

WEBSERVICE_DATASOURCE = False
DATA_SOURCE = "data"
WSTIMEOUT = 5


def current_data_code(data_code):
    """Sets the current data path."""
    Ojota.CURRENT_DATA_CODE = data_code


class Cache(object):

    def set(self, name, elems):
        setattr(self, name, elems)

    def get(self, name):
        return getattr(self, name)

    def __contains__(self, name):
        return hasattr(self, name)


class Relation(object):
    """Adds a relation to another object."""
    def __init__(self, attr_fk, to_class, related_name=None, ws_call=None,
                  plural_name=None):
        """Constructor for the relation class
        Arguments:
            attr_fk -- a String with the foreign key attribute name
            to_class -- the class that the relation makes reference to
            related_name -- the name of the attribute for the backward relation
                             Default None
            ws_call -- the name of the webservice command
            plural_name -- basename of ws_call, only needed if plural_name 
                           should be changed.
        """
        self.attr_fk = attr_fk
        self.to_class = to_class
        self.related_name = related_name
        self.ws_call = ws_call
        self.plural_name = plural_name

    def get_property(self):
        """Returns the property in which the relation will be referenced."""
        def _ws_inner(method_self):
            """Inner function to return the property for the relation."""
            _klass = self.to_class()
            self.__plural_name = _klass.__class__.plural_name
            self.__get_all_cmd = _klass.__class__.get_all_cmd
            if self.plural_name is not None:
                plural_name = self.plural_name
            else:
                plural_name = method_self.plural_name
            if not self.ws_call:
                _klass.__class__.get_all_cmd = self.ws_call
                ret = _klass.get(getattr(method_self, self.attr_fk))
            else:
                _klass.__class__.plural_name = "/".join(
                            (plural_name, getattr(method_self, self.attr_fk)))
                _klass.__class__.get_all_cmd = self.ws_call
                ret = _klass.all()
            _klass.__class__.plural_name = self.__plural_name
            _klass.__class__.get_all_cmd = self.__get_all_cmd
            return ret

        def _inner(method_self):
            """Inner function to return the property for the relation."""
            fk = getattr(method_self, self.attr_fk)
            return self.to_class.get(fk)

        if self.ws_call is not None:
            ret = property(_ws_inner)
        else:
            ret = property(_inner)
        return ret

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


class MetaOjota(type):
    """Metaclass for Ojota"""
    def __init__(self, *args, **kwargs):
        self.relations = {}
        for attr, value in self.__dict__.items():
            if isinstance(value, Relation):
                value.set_reversed_property(self)
                setattr(self, attr, value.get_property())
                self.relations[value.attr_fk] = (value.to_class, attr)
        return super(MetaOjota, self).__init__(*args, **kwargs)


class Ojota(object):
    """Base class to create instances of serialized data in the source files.
    """
    __metaclass__ = MetaOjota
    CURRENT_DATA_CODE = ''
    plural_name = 'Ojota'
    data_in_root = True
    pk_field = "pk"
    required_fields = None
    cache_class = Cache

    @property
    def primary_key(self):
        """Returns the primary key value."""
        return getattr(self, self.pk_field)

    def __init__(self, _pk=None, **kwargs):
        """Constructor."""
        self.fields = []
        if self.required_fields is not None:
            _requeridos = list(self.required_fields)
            _requeridos.append(self.pk_field)

            if not all([key in kwargs for key in _requeridos]):
                raise AttributeError
        for key, val in kwargs.iteritems():
            self.fields.append(key)
            setattr(self, key, val)

    @classmethod
    def _read_all_from_datasource(cls):
        """Reads the data from the datasource, makes a dictionary with the key
        specified in the key parameter. Allows to filter by subdirectories when
        the data is not on the root according to the data path."""
        cache_name = '_cache_' + cls.plural_name

        if not hasattr(cls, '__cache__'):
            cls.__cache__ = cls.cache_class()

        if not cls.data_in_root and Ojota.CURRENT_DATA_CODE:
            cache_name += '_' + Ojota.CURRENT_DATA_CODE

        if cache_name not in cls.__cache__:
            if cls.data_in_root or not Ojota.CURRENT_DATA_CODE:
                filepath = os.path.join(DATA_SOURCE,
                                         cls.plural_name)
            else:
                filepath = os.path.join(DATA_SOURCE,
                                         Ojota.CURRENT_DATA_CODE,
                                         cls.plural_name)
            if os.path.exists(filepath + '.json'):
                elements = cls._read_json_elements(filepath)
            elif os.path.exists(filepath + '.yaml'):
                elements = cls._read_yaml_elements(filepath)
            elif WEBSERVICE_DATASOURCE:
                elements = cls._read_ws_elements(url=filepath)
            else:
                raise Exception("Unknown datasource.")
            cls.__cache__.set(name=cache_name, elems=elements)
        return cls.__cache__.get(cache_name)

    @classmethod
    def _read_item_from_datasource(cls, pk):
        """Reads the data form the datasource if support index search."""
        cache_name = '_cache_' + cls.plural_name

        if not hasattr(cls, '__cache__'):
            cls.__cache__ = cls.cache_class()

        if not cls.data_in_root and Ojota.CURRENT_DATA_CODE:
            cache_name += '_' + Ojota.CURRENT_DATA_CODE

        if cls.data_in_root or not Ojota.CURRENT_DATA_CODE:
            filepath = os.path.join(DATA_SOURCE,
                                     cls.plural_name)
        else:
            filepath = os.path.join(DATA_SOURCE,
                                     Ojota.CURRENT_DATA_CODE,
                                     cls.plural_name)
        if WEBSERVICE_DATASOURCE:
            element = cls._read_ws_element(url=filepath, pk=pk)
        else:
            raise Exception("Unknown datasource.")

        if cache_name in cls.__cache__:
            __cache__ = cls.__cache__.get(cache_name)
            __cache__.update(element)
            cls.__cache__.set(name=cache_name, elems=__cache__)
        else:
            __cache__ = element
        return __cache__[pk]

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
    def _read_ws_elements(cls, url):
        _url = url + cls.get_all_cmd
        data = urlopen(_url, timeout=WSTIMEOUT).read()
        data = json.loads(data)
        elements = dict((element_data[cls.pk_field], element_data)
                        for element_data in data)
        return elements

    @classmethod
    def _read_ws_element(cls, url, pk):
        _url = "%s/%s%s" % (url, pk, cls.get_cmd)
        data = urlopen(_url, timeout=WSTIMEOUT).read()
        data = json.loads(data)
        element = {data[cls.pk_field]: data}
        return element

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
                r = str(element_data[field]).lower().startswith(
                                                            str(value).lower())
            elif operation == 'endswith':
                r = str(element_data[field]).endswith(str(value))
            elif operation == 'iendswith':
                r = str(element_data[field]).lower().endswith(
                                                            str(value).lower())
            elif operation == 'range':
                r = value[0] <= element_data[field] <= value[1]
            elif operation == 'ne':
                r = element_data[field] != value
            else:
                raise AttributeError("The operation %s does not exist" %
                                      operation)
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

            data_list = sorted(data_list, key=lambda e:
                               getattr(e, order_field), reverse=reverse)
        return data_list

    @classmethod
    def all(cls, **kargs):
        """Returns all the elements that match the conditions."""
        elements = cls._read_all_from_datasource().values()
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

    @classmethod
    def get(cls, pk=None, **kargs):
        """Returns the first element that matches the conditions."""
        if pk:
            kargs[cls.pk_field] = pk
        if kargs.keys() == [cls.pk_field]:
            pk = kargs[cls.pk_field]
            if hasattr(cls, 'get_cmd'):
                elem = cls._read_item_from_datasource(pk)
                return cls._objetize([elem])[0]
            else:
                all_elems = cls._read_all_from_datasource()
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

    def __eq__(self, other):
        """Compare the equality of two elements."""
        same_pk = self.primary_key == other.primary_key
        same_class = self.__class__ is other.__class__
        return same_pk and same_class

    def __repr__(self):
        """String representation of the elements."""
        return '%s<%s>' % (self.__class__.__name__, self.primary_key)
